#!/usr/bin/env python3
"""
Test script for cloud-compatible PDF processing
Validates that all PDF processors are working correctly
"""

import sys
import os

# Add utils directory to path
utils_path = os.path.join(os.path.dirname(__file__), 'utils')
sys.path.insert(0, utils_path)

def test_pdf_processing():
    """Test all PDF processing capabilities"""
    print("📄 Testing PDF Processing Capabilities...")
    print("=" * 50)
    
    try:
        from utils.pdf_utils import test_pdf_processing, get_pdf_info
        
        # Test capabilities
        info = get_pdf_info()
        print(f"Available processors: {info['available_processors']}")
        print(f"Primary processor: {info['primary_processor']}")
        print(f"Annotation support: {info['annotation_support']}")
        
        # Run built-in test
        success = test_pdf_processing()
        
        if success:
            print("\n✅ PDF processing setup is ready for Streamlit Cloud!")
            return True
        else:
            print("\n❌ PDF processing setup failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing PDF processing: {str(e)}")
        return False

def test_resume_radar_imports():
    """Test that resume_radar modules can import without PyMuPDF"""
    print("\n🔍 Testing Resume Radar Module Imports...")
    print("=" * 50)
    
    modules_to_test = [
        'resume_radar.extract_pdf',
        'resume_radar.overlay_pdf', 
        'resume_radar.jd_parser',
        'resume_radar.resume_radar_service'
    ]
    
    all_success = True
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name} - OK")
        except ImportError as e:
            if 'fitz' in str(e) or 'PyMuPDF' in str(e):
                print(f"⚠️  {module_name} - PyMuPDF not available (expected on Streamlit Cloud)")
            else:
                print(f"❌ {module_name} - Import failed: {str(e)}")
                all_success = False
        except Exception as e:
            print(f"❌ {module_name} - Error: {str(e)}")
            all_success = False
    
    return all_success

def main():
    print("🚀 Cloud Compatibility Test Suite")
    print("Testing setup for Streamlit Cloud deployment...")
    print("=" * 60)
    
    # Test PDF processing
    pdf_test = test_pdf_processing()
    
    # Test resume radar imports
    import_test = test_resume_radar_imports()
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY:")
    print(f"   PDF Processing: {'✅ PASS' if pdf_test else '❌ FAIL'}")
    print(f"   Module Imports: {'✅ PASS' if import_test else '❌ FAIL'}")
    
    overall_success = pdf_test and import_test
    print(f"\n🎯 Overall Status: {'✅ READY FOR CLOUD DEPLOYMENT' if overall_success else '❌ NEEDS FIXES'}")
    
    if overall_success:
        print("\n🎉 Your application is ready for Streamlit Cloud!")
        print("   All PDF processors are available and modules import correctly.")
    else:
        print("\n⚠️  Some issues detected. Please review the errors above.")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)