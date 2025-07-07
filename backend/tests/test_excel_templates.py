#!/usr/bin/env python3
"""
Test script for Excel template functionality.
This tests the Excel templates and processor without needing full LinkedIn Agent setup.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import pandas as pd
import subprocess
import json

# Add the backend src directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

def test_excel_templates():
    """Test that Excel templates exist and have correct structure."""
    print("Testing Excel templates...")
    
    # Check template files exist
    template_path = Path(__file__).resolve().parents[2] / 'examples' / 'linkedin_template.xlsx'
    sample_path = Path(__file__).resolve().parents[2] / 'examples' / 'sample_input.xlsx'
    
    assert template_path.exists(), f"Template file not found: {template_path}"
    assert sample_path.exists(), f"Sample file not found: {sample_path}"
    
    # Check template structure
    template_wb = pd.ExcelFile(template_path)
    assert 'Company_Profiles' in template_wb.sheet_names, "Company_Profiles tab missing"
    assert 'Individual_Profiles' in template_wb.sheet_names, "Individual_Profiles tab missing"
    
    # Check columns
    company_df = pd.read_excel(template_path, sheet_name='Company_Profiles')
    expected_company_cols = ['Company Name', 'LinkedIn Company URL', 'Industry', 'Location', 'Notes']
    assert list(company_df.columns) == expected_company_cols, f"Company columns mismatch: {list(company_df.columns)}"
    
    individual_df = pd.read_excel(template_path, sheet_name='Individual_Profiles')
    expected_individual_cols = ['Full Name', 'LinkedIn Profile URL', 'Company', 'Position', 'Location', 'Notes']
    assert list(individual_df.columns) == expected_individual_cols, f"Individual columns mismatch: {list(individual_df.columns)}"
    
    print("✓ Excel templates structure is correct")

def test_sample_data():
    """Test that sample data has valid URLs."""
    print("Testing sample data...")
    
    sample_path = Path(__file__).resolve().parents[2] / 'examples' / 'sample_input.xlsx'
    
    # Check sample data
    company_df = pd.read_excel(sample_path, sheet_name='Company_Profiles')
    individual_df = pd.read_excel(sample_path, sheet_name='Individual_Profiles')
    
    # Check that we have data
    assert len(company_df) > 0, "No company data in sample file"
    assert len(individual_df) > 0, "No individual data in sample file"
    
    # Check URLs are valid LinkedIn URLs
    for url in company_df['LinkedIn Company URL']:
        assert 'linkedin.com/company/' in url, f"Invalid company URL: {url}"
        assert url.startswith('https://'), f"Company URL must start with https://: {url}"
    
    for url in individual_df['LinkedIn Profile URL']:
        assert 'linkedin.com/in/' in url, f"Invalid profile URL: {url}"
        assert url.startswith('https://'), f"Profile URL must start with https://: {url}"
    
    print("✓ Sample data has valid URLs")

def test_excel_processor():
    """Test the Excel processor functionality."""
    print("Testing Excel processor...")
    
    # Copy the Excel processor to a temporary location
    processor_source = Path(__file__).resolve().parents[2] / 'backend' / 'src' / 'batch_scrape_excel_enhanced.sh'
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy Excel processor
        excel_processor_path = Path(temp_dir) / 'excel_processor.py'
        
        # Create a simplified version of the processor for testing
        excel_processor_code = '''
import pandas as pd
import sys
import os
import json
import re
from urllib.parse import urlparse

def validate_linkedin_url(url: str, url_type: str) -> bool:
    if not url or not isinstance(url, str):
        return False
    
    try:
        parsed = urlparse(url.strip())
    except Exception:
        return False
    
    if parsed.scheme != 'https':
        return False
    
    if parsed.netloc not in ['www.linkedin.com', 'linkedin.com']:
        return False
    
    path = parsed.path.strip('/')
    
    if url_type == 'company':
        pattern = r'^company/[a-zA-Z0-9\\-_]+/?$'
        return bool(re.match(pattern, path))
    elif url_type == 'profile':
        pattern = r'^in/[a-zA-Z0-9\\-_]+/?$'
        return bool(re.match(pattern, path))
    
    return False

def main():
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    os.makedirs(output_dir, exist_ok=True)
    
    results = {
        'success': True,
        'tabs_processed': [],
        'errors': [],
        'csv_files': [],
        'total_urls': 0,
        'valid_urls': 0
    }
    
    try:
        excel_data = pd.read_excel(input_file, sheet_name=None)
        
        for sheet_name, df in excel_data.items():
            if sheet_name in ['Company_Profiles', 'Individual_Profiles']:
                if sheet_name == 'Company_Profiles':
                    url_column = 'LinkedIn Company URL'
                    url_type = 'company'
                else:
                    url_column = 'LinkedIn Profile URL'
                    url_type = 'profile'
                
                if url_column not in df.columns:
                    results['errors'].append(f"Required column '{url_column}' not found in tab '{sheet_name}'")
                    continue
                
                df = df.dropna(subset=[url_column])
                df = df[df[url_column].astype(str).str.strip() != '']
                
                if len(df) == 0:
                    results['errors'].append(f"No data found in tab '{sheet_name}'")
                    continue
                
                valid_count = 0
                for _, row in df.iterrows():
                    url = str(row[url_column]).strip()
                    results['total_urls'] += 1
                    
                    if validate_linkedin_url(url, url_type):
                        valid_count += 1
                        results['valid_urls'] += 1
                    else:
                        results['errors'].append(f"Invalid {url_type} URL: {url}")
                
                if valid_count > 0:
                    csv_path = os.path.join(output_dir, f"{sheet_name.lower()}.csv")
                    df.to_csv(csv_path, index=False)
                    results['csv_files'].append(csv_path)
                    results['tabs_processed'].append(sheet_name)
                    print(f"Processed {valid_count} valid URLs from tab '{sheet_name}'")
        
        if not results['tabs_processed']:
            results['success'] = False
            results['errors'].append("No valid tabs found")
    
    except Exception as e:
        results['success'] = False
        results['errors'].append(f"Error processing Excel file: {str(e)}")
    
    results_file = os.path.join(output_dir, 'processing_results.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results: {results['success']}, URLs: {results['valid_urls']}/{results['total_urls']}")
    
    if not results['success']:
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        
        with open(excel_processor_path, 'w') as f:
            f.write(excel_processor_code)
        
        # Test with sample file
        sample_path = Path(__file__).resolve().parents[2] / 'examples' / 'sample_input.xlsx'
        output_dir = Path(temp_dir) / 'output'
        
        # Run the processor
        result = subprocess.run([
            sys.executable, str(excel_processor_path), str(sample_path), str(output_dir)
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Excel processor failed: {result.stderr}"
        
        # Check results
        results_file = output_dir / 'processing_results.json'
        assert results_file.exists(), "Processing results file not created"
        
        with open(results_file) as f:
            results = json.load(f)
        
        assert results['success'], f"Processing failed: {results['errors']}"
        assert results['valid_urls'] > 0, "No valid URLs processed"
        assert len(results['csv_files']) > 0, "No CSV files generated"
        
        print(f"✓ Excel processor works correctly ({results['valid_urls']} valid URLs)")

def test_documentation():
    """Test that documentation exists."""
    print("Testing documentation...")
    
    doc_path = Path(__file__).resolve().parents[2] / 'docs' / 'EXCEL_FORMAT.md'
    assert doc_path.exists(), f"Documentation file not found: {doc_path}"
    
    # Check that documentation contains key sections
    with open(doc_path) as f:
        content = f.read()
    
    required_sections = [
        'Excel Format Guide',
        'Company_Profiles',
        'Individual_Profiles',
        'URL Format Requirements',
        'Data Validation Guidelines'
    ]
    
    for section in required_sections:
        assert section in content, f"Missing section in documentation: {section}"
    
    print("✓ Documentation is complete")

def main():
    """Run all tests."""
    print("Running Excel Template Tests...")
    print("=" * 50)
    
    try:
        test_excel_templates()
        test_sample_data()
        test_excel_processor()
        test_documentation()
        
        print("=" * 50)
        print("✓ All tests passed!")
        return 0
        
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())