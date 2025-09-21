"""
Job Description Parser for Automated Resume Relevance Check System
Extracts structured information from job descriptions using LLM-powered parsing
"""

import json
import re
from typing import Dict, List, Optional, Union
from pathlib import Path
import fitz  # PyMuPDF
import docx
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class JobDescriptionParser:
    def __init__(self):
        """Initialize the JD parser with OpenRouter client"""
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        self.model = "openai/gpt-4o-mini"
        
        # JD parsing prompt
        self.jd_parsing_prompt = """You are an expert HR recruiter and job analyst. Parse the following job description and extract structured information.

Extract and return ONLY a valid JSON object with these exact keys:
- role_title: The main job title/position name
- company: Company name (if mentioned)
- location: Job location (if mentioned) 
- must_have_skills: List of absolutely required technical skills, tools, languages
- good_to_have_skills: List of preferred/nice-to-have technical skills
- qualifications: List of education/certification/experience requirements
- responsibilities: List of key job responsibilities/duties
- experience_years: Number of years experience required (extract number, or null if not specified)

Be precise and extract only what's explicitly mentioned. Return clean, normalized skill names.

Job Description:
{jd_text}

Return only the JSON object:"""

    def extract_text_from_file(self, file_path: Union[str, Path]) -> str:
        """Extract text from PDF or DOCX file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            return self._extract_from_docx(file_path)
        else:
            # Assume it's a text file
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    def _extract_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF using PyMuPDF"""
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    
    def _extract_from_docx(self, docx_path: Path) -> str:
        """Extract text from DOCX file"""
        doc = docx.Document(docx_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def clean_jd_text(self, text: str) -> str:
        """Clean and normalize job description text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might interfere with parsing
        text = re.sub(r'[^\w\s\-\.\,\:\;\(\)\[\]/&+#]', ' ', text)
        return text.strip()
    
    def parse_jd_with_llm(self, jd_text: str) -> Dict:
        """Parse job description using LLM"""
        try:
            # Clean the text
            clean_text = self.clean_jd_text(jd_text)
            
            # Format prompt
            prompt = self.jd_parsing_prompt.format(jd_text=clean_text)
            
            # Call OpenRouter API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=1500
            )
            
            # Extract and parse JSON response
            response_text = response.choices[0].message.content.strip()
            
            # Clean response if it has markdown formatting
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            parsed_data = json.loads(response_text)
            
            # Validate required fields
            required_fields = ['role_title', 'must_have_skills', 'good_to_have_skills', 'qualifications']
            for field in required_fields:
                if field not in parsed_data:
                    parsed_data[field] = [] if field != 'role_title' else "Unknown Role"
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text}")
            # Return basic structure on error
            return self._create_fallback_structure(jd_text)
        except Exception as e:
            print(f"Error parsing JD: {e}")
            return self._create_fallback_structure(jd_text)
    
    def _create_fallback_structure(self, jd_text: str) -> Dict:
        """Create basic structure when LLM parsing fails"""
        return {
            "role_title": "Unable to parse role",
            "company": None,
            "location": None,
            "must_have_skills": [],
            "good_to_have_skills": [],
            "qualifications": [],
            "responsibilities": [],
            "experience_years": None,
            "raw_text": jd_text[:500] + "..." if len(jd_text) > 500 else jd_text
        }
    
    def parse_job_description(self, file_path: Union[str, Path] = None, text: str = None) -> Dict:
        """
        Main method to parse a job description
        
        Args:
            file_path: Path to JD file (PDF/DOCX/TXT)
            text: Raw JD text (alternative to file)
        
        Returns:
            Dict with parsed JD information
        """
        if file_path:
            jd_text = self.extract_text_from_file(file_path)
        elif text:
            jd_text = text
        else:
            raise ValueError("Either file_path or text must be provided")
        
        if not jd_text.strip():
            raise ValueError("No text content found in job description")
        
        # Parse with LLM
        parsed_jd = self.parse_jd_with_llm(jd_text)
        
        # Add metadata
        parsed_jd['_metadata'] = {
            'source': str(file_path) if file_path else 'text_input',
            'text_length': len(jd_text),
            'parsed_successfully': bool(parsed_jd.get('role_title') and parsed_jd['role_title'] != "Unable to parse role")
        }
        
        return parsed_jd
    
    def get_all_skills(self, parsed_jd: Dict) -> List[str]:
        """Get all skills (must-have + good-to-have) from parsed JD"""
        must_have = parsed_jd.get('must_have_skills', [])
        good_to_have = parsed_jd.get('good_to_have_skills', [])
        return must_have + good_to_have
    
    def print_parsed_jd(self, parsed_jd: Dict):
        """Pretty print parsed job description"""
        print("=" * 60)
        print("PARSED JOB DESCRIPTION")
        print("=" * 60)
        print(f"Role: {parsed_jd.get('role_title', 'Unknown')}")
        print(f"Company: {parsed_jd.get('company', 'Not specified')}")
        print(f"Location: {parsed_jd.get('location', 'Not specified')}")
        print(f"Experience: {parsed_jd.get('experience_years', 'Not specified')} years")
        
        print(f"\nMust-Have Skills ({len(parsed_jd.get('must_have_skills', []))})")
        for skill in parsed_jd.get('must_have_skills', []):
            print(f"  • {skill}")
        
        print(f"\nGood-to-Have Skills ({len(parsed_jd.get('good_to_have_skills', []))})")
        for skill in parsed_jd.get('good_to_have_skills', []):
            print(f"  • {skill}")
        
        print(f"\nQualifications ({len(parsed_jd.get('qualifications', []))})")
        for qual in parsed_jd.get('qualifications', []):
            print(f"  • {qual}")
        
        print(f"\nKey Responsibilities ({len(parsed_jd.get('responsibilities', []))})")
        for resp in parsed_jd.get('responsibilities', [])[:3]:  # Show first 3
            print(f"  • {resp}")
        
        print("=" * 60)


if __name__ == "__main__":
    # Test the JD parser
    parser = JobDescriptionParser()
    
    # Test with sample JD text
    sample_jd = """
    Data Scientist - Machine Learning Engineer
    Company: TechCorp Solutions
    Location: Bangalore, India
    
    We are looking for a skilled Data Scientist to join our AI team.
    
    Required Skills:
    - Python programming (3+ years)
    - Machine Learning frameworks (scikit-learn, TensorFlow, PyTorch)
    - SQL and database management
    - Statistical analysis and data visualization
    - Experience with cloud platforms (AWS/GCP/Azure)
    
    Preferred Skills:
    - Deep Learning and Neural Networks
    - Big Data tools (Spark, Hadoop)
    - Docker and Kubernetes
    - MLOps and model deployment
    
    Qualifications:
    - Bachelor's/Master's in Computer Science, Statistics, or related field
    - 3-5 years of experience in data science
    - Strong problem-solving skills
    
    Responsibilities:
    - Develop and deploy machine learning models
    - Analyze large datasets to extract insights
    - Collaborate with engineering teams
    - Present findings to stakeholders
    """
    
    try:
        result = parser.parse_job_description(text=sample_jd)
        parser.print_parsed_jd(result)
    except Exception as e:
        print(f"Error testing JD parser: {e}")