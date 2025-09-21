"""
Resume-JD Matching Engine for Automated Resume Relevance Check System
Implements both hard matching (keywords) and soft matching (semantic similarity)
"""

import json
import re
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path
import numpy as np
from difflib import SequenceMatcher
from collections import Counter
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class ResumeJDMatcher:
    def __init__(self):
        """Initialize the matching engine"""
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        self.model = "openai/gpt-4o-mini"
        
        # Fuzzy matching threshold
        self.fuzzy_threshold = 0.8
        
        # Common skill aliases for better matching
        self.skill_aliases = {
            'python': ['python3', 'py', 'python programming'],
            'javascript': ['js', 'node.js', 'nodejs', 'react', 'angular', 'vue'],
            'sql': ['mysql', 'postgresql', 'sqlite', 'database'],
            'machine learning': ['ml', 'artificial intelligence', 'ai', 'data science'],
            'tensorflow': ['tf', 'keras'],
            'pytorch': ['torch'],
            'aws': ['amazon web services', 'ec2', 's3', 'lambda'],
            'docker': ['containerization', 'containers'],
            'kubernetes': ['k8s', 'container orchestration'],
            'git': ['version control', 'github', 'gitlab'],
            'api': ['rest api', 'restful', 'web services'],
            'agile': ['scrum', 'kanban'],
            'html': ['html5', 'markup'],
            'css': ['css3', 'styling', 'bootstrap'],
            'java': ['java8', 'java11', 'spring'],
        }
        
        # Semantic similarity prompt
        self.similarity_prompt = """You are an expert HR recruiter analyzing resume-job fit.

Compare this resume with the job requirements and rate the semantic similarity on a scale of 0-100.

Focus on:
- Overall role fit and experience alignment
- Technical skills overlap (even if not exact matches)
- Industry/domain relevance
- Career level appropriateness
- Transferable skills

Job Description Summary:
Role: {role_title}
Must-Have Skills: {must_have_skills}
Good-to-Have Skills: {good_to_have_skills}
Experience Required: {experience_years} years

Resume Content:
{resume_text}

Rate the semantic fit from 0-100 where:
- 90-100: Perfect fit, highly relevant experience
- 75-89: Strong fit, most requirements met
- 60-74: Good fit, some skill gaps but promising
- 45-59: Moderate fit, significant training needed
- 30-44: Weak fit, major gaps in requirements
- 0-29: Poor fit, not suitable for this role

Provide ONLY a number (0-100):"""

    def normalize_skill(self, skill: str) -> str:
        """Normalize skill text for better matching"""
        skill = skill.lower().strip()
        # Remove common prefixes/suffixes
        skill = re.sub(r'\b(programming|language|framework|library|tool|platform)\b', '', skill)
        # Remove parentheses and their contents
        skill = re.sub(r'\([^)]*\)', '', skill)
        # Clean up whitespace
        skill = re.sub(r'\s+', ' ', skill).strip()
        return skill

    def expand_skill_aliases(self, skill: str) -> List[str]:
        """Get all possible aliases for a skill"""
        normalized = self.normalize_skill(skill)
        aliases = [normalized]
        
        for main_skill, alias_list in self.skill_aliases.items():
            if normalized == main_skill or normalized in alias_list:
                aliases.extend([main_skill] + alias_list)
        
        return list(set(aliases))

    def fuzzy_match_score(self, text1: str, text2: str) -> float:
        """Calculate fuzzy matching score between two strings"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def extract_resume_skills(self, resume_text: str) -> List[str]:
        """Extract skills from resume text using basic patterns"""
        # Common skill indicators
        skill_patterns = [
            r'(?i)skills?[:\-\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
            r'(?i)technologies?[:\-\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
            r'(?i)programming languages?[:\-\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
            r'(?i)tools?[:\-\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
            r'(?i)frameworks?[:\-\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
        ]
        
        skills = []
        for pattern in skill_patterns:
            matches = re.findall(pattern, resume_text, re.MULTILINE | re.DOTALL)
            for match in matches:
                # Split by common delimiters
                skill_list = re.split(r'[,;•\-\n\|]', match)
                for skill in skill_list:
                    clean_skill = self.normalize_skill(skill)
                    if len(clean_skill) > 2:  # Ignore very short matches
                        skills.append(clean_skill)
        
        return list(set(skills))

    def hard_match_analysis(self, resume_text: str, jd_skills: List[str]) -> Dict:
        """Perform keyword-based hard matching"""
        resume_skills = self.extract_resume_skills(resume_text)
        resume_text_lower = resume_text.lower()
        
        exact_matches = []
        fuzzy_matches = []
        missing_skills = []
        
        for jd_skill in jd_skills:
            jd_skill_normalized = self.normalize_skill(jd_skill)
            skill_aliases = self.expand_skill_aliases(jd_skill_normalized)
            
            found_exact = False
            found_fuzzy = False
            
            # Check for exact matches (including aliases)
            for alias in skill_aliases:
                if alias in resume_text_lower:
                    exact_matches.append(jd_skill)
                    found_exact = True
                    break
            
            if not found_exact:
                # Check for fuzzy matches
                best_fuzzy_score = 0
                for resume_skill in resume_skills:
                    for alias in skill_aliases:
                        fuzzy_score = self.fuzzy_match_score(resume_skill, alias)
                        if fuzzy_score > best_fuzzy_score:
                            best_fuzzy_score = fuzzy_score
                
                if best_fuzzy_score >= self.fuzzy_threshold:
                    fuzzy_matches.append({
                        'jd_skill': jd_skill,
                        'score': best_fuzzy_score
                    })
                    found_fuzzy = True
            
            if not found_exact and not found_fuzzy:
                missing_skills.append(jd_skill)
        
        return {
            'exact_matches': exact_matches,
            'fuzzy_matches': fuzzy_matches,
            'missing_skills': missing_skills,
            'total_jd_skills': len(jd_skills),
            'hard_match_score': (len(exact_matches) + len(fuzzy_matches)) / len(jd_skills) * 100 if jd_skills else 0
        }

    def semantic_match_analysis(self, resume_text: str, parsed_jd: Dict) -> float:
        """Perform LLM-based semantic matching"""
        try:
            # Format the prompt
            prompt = self.similarity_prompt.format(
                role_title=parsed_jd.get('role_title', 'Unknown'),
                must_have_skills=', '.join(parsed_jd.get('must_have_skills', [])),
                good_to_have_skills=', '.join(parsed_jd.get('good_to_have_skills', [])),
                experience_years=parsed_jd.get('experience_years', 'Not specified'),
                resume_text=resume_text[:3000]  # Limit text length
            )
            
            # Call OpenRouter API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=50
            )
            
            # Extract score
            response_text = response.choices[0].message.content.strip()
            
            # Extract number from response
            score_match = re.search(r'\b(\d{1,3})\b', response_text)
            if score_match:
                score = int(score_match.group(1))
                return min(max(score, 0), 100)  # Clamp to 0-100
            else:
                print(f"Could not extract score from: {response_text}")
                return 50.0  # Default fallback
                
        except Exception as e:
            print(f"Error in semantic analysis: {e}")
            return 50.0  # Default fallback

    def calculate_relevance_score(self, hard_match_result: Dict, semantic_score: float, 
                                parsed_jd: Dict) -> Dict:
        """Calculate final relevance score combining hard and semantic matches"""
        
        # Weight factors
        must_have_weight = 0.4  # 40% for must-have skills
        good_to_have_weight = 0.2  # 20% for good-to-have skills  
        semantic_weight = 0.4   # 40% for semantic similarity
        
        # Calculate must-have vs good-to-have performance
        must_have_skills = parsed_jd.get('must_have_skills', [])
        good_to_have_skills = parsed_jd.get('good_to_have_skills', [])
        
        # Separate matching for must-have vs good-to-have
        must_have_matches = 0
        good_to_have_matches = 0
        
        for skill in hard_match_result['exact_matches']:
            if skill in must_have_skills:
                must_have_matches += 1
            elif skill in good_to_have_skills:
                good_to_have_matches += 1
        
        for fuzzy_match in hard_match_result['fuzzy_matches']:
            skill = fuzzy_match['jd_skill']
            if skill in must_have_skills:
                must_have_matches += 1
            elif skill in good_to_have_skills:
                good_to_have_matches += 1
        
        # Calculate component scores
        must_have_score = (must_have_matches / len(must_have_skills) * 100) if must_have_skills else 100
        good_to_have_score = (good_to_have_matches / len(good_to_have_skills) * 100) if good_to_have_skills else 100
        
        # Final weighted score
        final_score = (
            must_have_score * must_have_weight +
            good_to_have_score * good_to_have_weight +
            semantic_score * semantic_weight
        )
        
        return {
            'relevance_score': round(final_score, 1),
            'must_have_score': round(must_have_score, 1),
            'good_to_have_score': round(good_to_have_score, 1),
            'semantic_score': semantic_score,
            'score_breakdown': {
                'must_have_weight': must_have_weight,
                'good_to_have_weight': good_to_have_weight,
                'semantic_weight': semantic_weight
            }
        }

    def get_verdict(self, relevance_score: float) -> str:
        """Determine High/Medium/Low verdict based on relevance score"""
        if relevance_score >= 75:
            return "High"
        elif relevance_score >= 50:
            return "Medium"  
        else:
            return "Low"

    def analyze_resume_jd_match(self, resume_text: str, parsed_jd: Dict) -> Dict:
        """
        Main method to analyze resume against job description
        
        Args:
            resume_text: Full resume text content
            parsed_jd: Parsed job description from JDParser
            
        Returns:
            Complete matching analysis results
        """
        # Get all JD skills
        all_jd_skills = parsed_jd.get('must_have_skills', []) + parsed_jd.get('good_to_have_skills', [])
        
        # Perform hard matching
        print("🔍 Performing hard match analysis...")
        hard_match_result = self.hard_match_analysis(resume_text, all_jd_skills)
        
        # Perform semantic matching
        print("🧠 Performing semantic match analysis...")
        semantic_score = self.semantic_match_analysis(resume_text, parsed_jd)
        
        # Calculate final relevance score
        print("📊 Calculating relevance score...")
        score_result = self.calculate_relevance_score(hard_match_result, semantic_score, parsed_jd)
        
        # Get verdict
        verdict = self.get_verdict(score_result['relevance_score'])
        
        # Combine all results
        analysis_result = {
            'job_role': parsed_jd.get('role_title', 'Unknown'),
            'relevance_score': score_result['relevance_score'],
            'verdict': verdict,
            'hard_match': hard_match_result,
            'semantic_score': semantic_score,
            'score_breakdown': score_result,
            'missing_skills': hard_match_result['missing_skills'],
            'matched_skills': hard_match_result['exact_matches'],
            'fuzzy_matched_skills': [fm['jd_skill'] for fm in hard_match_result['fuzzy_matches']],
            'analysis_summary': {
                'total_skills_required': len(all_jd_skills),
                'skills_matched': len(hard_match_result['exact_matches']) + len(hard_match_result['fuzzy_matches']),
                'skills_missing': len(hard_match_result['missing_skills']),
                'match_percentage': round((len(hard_match_result['exact_matches']) + len(hard_match_result['fuzzy_matches'])) / len(all_jd_skills) * 100, 1) if all_jd_skills else 0
            }
        }
        
        return analysis_result

    def print_match_analysis(self, analysis_result: Dict):
        """Pretty print matching analysis results"""
        print("=" * 70)
        print("RESUME-JD MATCHING ANALYSIS")
        print("=" * 70)
        print(f"Job Role: {analysis_result['job_role']}")
        print(f"Relevance Score: {analysis_result['relevance_score']}/100")
        print(f"Verdict: {analysis_result['verdict']}")
        print(f"Semantic Similarity: {analysis_result['semantic_score']}/100")
        
        print(f"\n📊 SCORE BREAKDOWN:")
        breakdown = analysis_result['score_breakdown']
        print(f"  Must-Have Skills: {breakdown['must_have_score']}/100")
        print(f"  Good-to-Have Skills: {breakdown['good_to_have_score']}/100")
        print(f"  Semantic Match: {breakdown['semantic_score']}/100")
        
        print(f"\n✅ MATCHED SKILLS ({len(analysis_result['matched_skills'])}):")
        for skill in analysis_result['matched_skills']:
            print(f"  • {skill}")
        
        if analysis_result['fuzzy_matched_skills']:
            print(f"\n⚡ FUZZY MATCHED SKILLS ({len(analysis_result['fuzzy_matched_skills'])}):")
            for skill in analysis_result['fuzzy_matched_skills']:
                print(f"  • {skill}")
        
        if analysis_result['missing_skills']:
            print(f"\n❌ MISSING SKILLS ({len(analysis_result['missing_skills'])}):")
            for skill in analysis_result['missing_skills']:
                print(f"  • {skill}")
        
        summary = analysis_result['analysis_summary']
        print(f"\n📋 SUMMARY:")
        print(f"  Skills Required: {summary['total_skills_required']}")
        print(f"  Skills Matched: {summary['skills_matched']}")
        print(f"  Skills Missing: {summary['skills_missing']}")
        print(f"  Match Rate: {summary['match_percentage']}%")
        
        print("=" * 70)


if __name__ == "__main__":
    # Test the matching engine
    from jd_parser import JobDescriptionParser
    
    # Sample JD and resume for testing
    sample_jd = """
    Data Scientist Position
    Required: Python, Machine Learning, SQL, Statistics
    Preferred: TensorFlow, AWS, Docker
    Experience: 3+ years
    """
    
    sample_resume = """
    John Doe
    Data Analyst with 4 years experience
    
    Skills:
    - Python programming (5 years)
    - SQL databases (MySQL, PostgreSQL)  
    - Statistical analysis and modeling
    - Machine learning algorithms
    - Data visualization (matplotlib, seaborn)
    - Git version control
    
    Experience:
    Senior Data Analyst at Tech Corp (2020-2024)
    - Developed ML models for customer segmentation
    - Built ETL pipelines using Python
    - Created dashboards for business insights
    """
    
    try:
        # Parse JD
        jd_parser = JobDescriptionParser()
        parsed_jd = jd_parser.parse_job_description(text=sample_jd)
        
        # Analyze match
        matcher = ResumeJDMatcher()
        result = matcher.analyze_resume_jd_match(sample_resume, parsed_jd)
        
        # Print results
        matcher.print_match_analysis(result)
        
    except Exception as e:
        print(f"Error testing matcher: {e}")