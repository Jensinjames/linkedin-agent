#!/usr/bin/env bash
set -euo pipefail

# ======== ENHANCED BATCH EXCEL PROCESSOR ========
# This script processes Excel files with multiple tabs and URL validation
# Supports both Company_Profiles and Individual_Profiles tabs
# ================================================

# Configuration
INPUT_FILE="${1:-input.xlsx}"      # Accepts .xlsx or .csv
INPUT_JSON_TEMPLATE="${2:-input.json}" # The input.json template to use
LOG_DIR="${3:-batch_logs}"         # Where logs and batch outputs go
BATCH_SIZE=10000                   # URLs per batch
MAX_RETRIES=3                      # How many times to retry a failed batch
FINAL_OUTPUT="$LOG_DIR/output_all.xlsx"

# Create directories
mkdir -p "$LOG_DIR/batches" "$LOG_DIR/outputs" "$LOG_DIR/processed"

# Logging function
status() { echo -e "[$(date +"%F %T")] $*"; }
log_file="$LOG_DIR/batch_run.log"
touch "$log_file"

# Copy Excel processor to a accessible location
EXCEL_PROCESSOR="$LOG_DIR/excel_processor.py"
cat > "$EXCEL_PROCESSOR" << 'EOF'
#!/usr/bin/env python3
"""
Enhanced Excel processor for LinkedIn Agent that handles multiple tabs and URL validation.
"""

import pandas as pd
import sys
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse

def validate_linkedin_url(url: str, url_type: str) -> bool:
    """
    Validate LinkedIn URL format.
    
    Args:
        url: The URL to validate
        url_type: 'company' or 'profile'
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    # Parse URL
    try:
        parsed = urlparse(url.strip())
    except Exception:
        return False
    
    # Check basic structure
    if not parsed.scheme or not parsed.netloc:
        return False
    
    # Must be HTTPS LinkedIn
    if parsed.scheme != 'https':
        return False
    
    if parsed.netloc not in ['www.linkedin.com', 'linkedin.com']:
        return False
    
    # Check path structure
    path = parsed.path.strip('/')
    
    if url_type == 'company':
        # Company URL: /company/[company-name]/
        pattern = r'^company/[a-zA-Z0-9\-_]+/?$'
        return bool(re.match(pattern, path))
    
    elif url_type == 'profile':
        # Profile URL: /in/[profile-name]/
        pattern = r'^in/[a-zA-Z0-9\-_]+/?$'
        return bool(re.match(pattern, path))
    
    return False

def process_excel_file(file_path: str, output_dir: str) -> Dict:
    """
    Process Excel file with multiple tabs and URL validation.
    
    Args:
        file_path: Path to the Excel file
        output_dir: Directory to save processed CSV files
    
    Returns:
        Dict with processing results
    """
    results = {
        'success': True,
        'tabs_processed': [],
        'errors': [],
        'csv_files': [],
        'total_urls': 0,
        'valid_urls': 0
    }
    
    try:
        # Read all sheets
        excel_data = pd.read_excel(file_path, sheet_name=None)
        
        # Process each tab
        for sheet_name, df in excel_data.items():
            if sheet_name in ['Company_Profiles', 'Individual_Profiles']:
                csv_file = process_tab(df, sheet_name, output_dir, results)
                if csv_file:
                    results['csv_files'].append(csv_file)
                    results['tabs_processed'].append(sheet_name)
            else:
                results['errors'].append(f"Unknown tab '{sheet_name}' - only 'Company_Profiles' and 'Individual_Profiles' are supported")
        
        if not results['tabs_processed']:
            results['success'] = False
            results['errors'].append("No valid tabs found. Expected 'Company_Profiles' and/or 'Individual_Profiles'")
    
    except Exception as e:
        results['success'] = False
        results['errors'].append(f"Error processing Excel file: {str(e)}")
    
    return results

def process_tab(df: pd.DataFrame, tab_name: str, output_dir: str, results: Dict) -> Optional[str]:
    """
    Process a single tab from the Excel file.
    
    Args:
        df: DataFrame containing the tab data
        tab_name: Name of the tab ('Company_Profiles' or 'Individual_Profiles')
        output_dir: Directory to save the CSV file
        results: Results dictionary to update
    
    Returns:
        str: Path to the generated CSV file, or None if processing failed
    """
    try:
        # Determine the required URL column
        if tab_name == 'Company_Profiles':
            url_column = 'LinkedIn Company URL'
            url_type = 'company'
        elif tab_name == 'Individual_Profiles':
            url_column = 'LinkedIn Profile URL'
            url_type = 'profile'
        else:
            results['errors'].append(f"Unknown tab type: {tab_name}")
            return None
        
        # Check if required column exists
        if url_column not in df.columns:
            results['errors'].append(f"Required column '{url_column}' not found in tab '{tab_name}'")
            return None
        
        # Remove empty rows
        df = df.dropna(subset=[url_column])
        df = df[df[url_column].astype(str).str.strip() != '']
        
        if len(df) == 0:
            results['errors'].append(f"No data found in tab '{tab_name}'")
            return None
        
        # Validate URLs
        valid_rows = []
        for idx, row in df.iterrows():
            url = str(row[url_column]).strip()
            results['total_urls'] += 1
            
            if validate_linkedin_url(url, url_type):
                valid_rows.append(row)
                results['valid_urls'] += 1
            else:
                results['errors'].append(f"Invalid {url_type} URL in tab '{tab_name}': {url}")
        
        if not valid_rows:
            results['errors'].append(f"No valid URLs found in tab '{tab_name}'")
            return None
        
        # Create DataFrame with valid rows
        valid_df = pd.DataFrame(valid_rows)
        
        # Save to CSV
        csv_filename = f"{tab_name.lower()}.csv"
        csv_path = os.path.join(output_dir, csv_filename)
        
        # Create a simplified CSV with just the URL for batch processing
        batch_df = pd.DataFrame({
            'url': valid_df[url_column],
            'type': url_type,
            'source_tab': tab_name
        })
        
        batch_df.to_csv(csv_path, index=False)
        
        print(f"Processed {len(valid_df)} valid URLs from tab '{tab_name}' -> {csv_path}")
        
        return csv_path
        
    except Exception as e:
        results['errors'].append(f"Error processing tab '{tab_name}': {str(e)}")
        return None

def main():
    """Main function to process Excel file."""
    if len(sys.argv) < 3:
        print("Usage: python excel_processor.py <input_file.xlsx> <output_dir>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Process Excel file
    results = process_excel_file(input_file, output_dir)
    
    # Print results
    print(f"\nProcessing Results:")
    print(f"Success: {results['success']}")
    print(f"Tabs processed: {results['tabs_processed']}")
    print(f"Total URLs: {results['total_urls']}")
    print(f"Valid URLs: {results['valid_urls']}")
    print(f"CSV files created: {len(results['csv_files'])}")
    
    if results['errors']:
        print(f"\nErrors ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"  - {error}")
    
    if results['csv_files']:
        print(f"\nGenerated CSV files:")
        for csv_file in results['csv_files']:
            print(f"  - {csv_file}")
    
    # Save results to JSON
    results_file = os.path.join(output_dir, 'processing_results.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nProcessing results saved to: {results_file}")
    
    # Exit with error code if processing failed
    if not results['success']:
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

# Make it executable
chmod +x "$EXCEL_PROCESSOR"

# Process input file
status "Processing input file: $INPUT_FILE"

if [[ "$INPUT_FILE" == *.xlsx ]] || [[ "$INPUT_FILE" == *.xls ]]; then
    # Process Excel file with multiple tabs
    status "Processing Excel file with multiple tabs and URL validation..."
    if ! python3 "$EXCEL_PROCESSOR" "$INPUT_FILE" "$LOG_DIR/processed" 2>&1 | tee -a "$log_file"; then
        status "Excel processing failed. Check logs for details."
        exit 1
    fi
    
    # Get list of generated CSV files
    CSV_FILES=($(find "$LOG_DIR/processed" -name "*.csv" 2>/dev/null))
    
    if [[ ${#CSV_FILES[@]} -eq 0 ]]; then
        status "No CSV files generated from Excel processing. Aborting."
        exit 1
    fi
    
    status "Generated ${#CSV_FILES[@]} CSV files for batch processing"
    
elif [[ "$INPUT_FILE" == *.csv ]]; then
    # Handle single CSV file (legacy support)
    status "Processing single CSV file (legacy mode)..."
    CSV_FILES=("$INPUT_FILE")
    
    # Simple URL validation for CSV
    if ! python3 -c "
import pandas as pd
import sys
df = pd.read_csv('$INPUT_FILE')
if df.empty:
    print('CSV file is empty')
    sys.exit(1)
print(f'CSV file contains {len(df)} rows')
" 2>&1 | tee -a "$log_file"; then
        status "CSV validation failed"
        exit 1
    fi
else
    status "Input file must be .xlsx, .xls, or .csv"
    exit 1
fi

# Process each CSV file
PROGRESS_FILE="$LOG_DIR/batch_progress.txt"
touch "$PROGRESS_FILE"

total_batches=0
processed_batches=0

for csv_file in "${CSV_FILES[@]}"; do
    csv_basename=$(basename "$csv_file" .csv)
    status "Processing CSV file: $csv_basename"
    
    # Split CSV into batches
    status "Splitting $csv_basename into batches of $BATCH_SIZE..."
    split -l $BATCH_SIZE -d --additional-suffix=.csv "$csv_file" "$LOG_DIR/batches/${csv_basename}_batch_"
    
    # Process each batch
    for batch_csv in "$LOG_DIR"/batches/${csv_basename}_batch_*.csv; do
        batch_id=$(basename "$batch_csv" .csv)
        batch_json="$LOG_DIR/batches/${batch_id}.json"
        batch_output="$LOG_DIR/outputs/${batch_id}_output.json"
        batch_xlsx="$LOG_DIR/outputs/${batch_id}_output.xlsx"
        
        total_batches=$((total_batches + 1))
        
        # Skip if already processed
        if grep -q "^$batch_id$" "$PROGRESS_FILE"; then
            status "Skipping $batch_id (already completed)" | tee -a "$log_file"
            processed_batches=$((processed_batches + 1))
            continue
        fi
        
        # Prepare per-batch input.json
        jq ".inputType=\"csv\" | .inputPath=\"$batch_csv\"" "$INPUT_JSON_TEMPLATE" > "$batch_json"
        
        # Retry up to MAX_RETRIES times
        for try in $(seq 1 $MAX_RETRIES); do
            status "Processing $batch_id (try $try of $MAX_RETRIES)..." | tee -a "$log_file"
            if python3 -m src.cli "$batch_json" > "$batch_output" 2>>"$log_file"; then
                # Convert JSON to Excel
                status "Converting $batch_id output to Excel..." | tee -a "$log_file"
                python3 -c "
import sys, json, pandas as pd
with open(sys.argv[1]) as f:
    data = json.load(f)
# If wrapped in a dict
if isinstance(data, dict) and 'results' in data:
    records = data['results']
else:
    records = data
if not records:
    pd.DataFrame().to_excel(sys.argv[2], index=False)
else:
    # Reformat as CRM columns, flattening as needed
    def get(x, key):
        return x.get(key) or ''
    out = []
    for x in records:
        out.append({
            'Full Name': get(x, 'name'),
            'Headline': get(x, 'headline'),
            'Company': get(x, 'company') or get(x, 'company_name'),
            'Location': get(x, 'location'),
            'Connections': get(x, 'connections'),
            'About': get(x, 'about'),
            'Experience': str(get(x, 'experience') or ''),
            'Education': str(get(x, 'education') or ''),
            'Skills': ', '.join(get(x, 'skills') or []) if isinstance(get(x, 'skills'), list) else (get(x, 'skills') or '')
        })
    pd.DataFrame(out).to_excel(sys.argv[2], index=False)
" "$batch_output" "$batch_xlsx"
                
                echo "$batch_id" >> "$PROGRESS_FILE"
                processed_batches=$((processed_batches + 1))
                status "Batch $batch_id completed ($processed_batches/$total_batches)." | tee -a "$log_file"
                break
            else
                status "Batch $batch_id failed on try $try." | tee -a "$log_file"
                if [[ $try -lt $MAX_RETRIES ]]; then
                    sleep $((try*10))
                fi
            fi
        done
        
        # If not successful after retries, mark as failed
        if ! grep -q "^$batch_id$" "$PROGRESS_FILE"; then
            status "Batch $batch_id failed after $MAX_RETRIES tries, aborting." | tee -a "$log_file"
            exit 1
        fi
    done
done

# Merge all Excel outputs
status "Merging all batch Excel files to $FINAL_OUTPUT..."
python3 -c "
import glob, pandas as pd, os
files = sorted(glob.glob('$LOG_DIR/outputs/*_output.xlsx'))
print(f'Found {len(files)} Excel files to merge')
dfs = []
for f in files:
    if os.path.getsize(f) > 0:
        try:
            df = pd.read_excel(f)
            if not df.empty:
                dfs.append(df)
        except Exception as e:
            print(f'Error reading {f}: {e}')
            
if dfs:
    merged = pd.concat(dfs, ignore_index=True)
    merged.to_excel('$FINAL_OUTPUT', index=False)
    print(f'Merged {len(dfs)} files into {\"$FINAL_OUTPUT\"} with {len(merged)} total records')
else:
    print('No results to merge.')
    pd.DataFrame().to_excel('$FINAL_OUTPUT', index=False)
"

status "Batch processing complete!"
status "Total batches processed: $processed_batches/$total_batches"
status "Final output: $FINAL_OUTPUT"
status "Processing results and logs available in: $LOG_DIR"