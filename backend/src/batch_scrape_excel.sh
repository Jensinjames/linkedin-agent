# See prior message for full code (bash script for batch Excel chunking and job submission)
# Place in src/batch_scrape_excel.sh
#!/usr/bin/env bash
set -euo pipefail

# ======== CONFIGURATION ========
INPUT_FILE="${1:-input.xlsx}"      # Accepts .xlsx or .csv
INPUT_JSON_TEMPLATE="${2:-input.json}" # The input.json template to use
LOG_DIR="${3:-batch_logs}"         # Where logs and batch outputs go
BATCH_SIZE=10000                   # 10k per batch
MAX_RETRIES=3                      # How many times to retry a failed batch
FINAL_OUTPUT="$LOG_DIR/output_all.xlsx"
COLUMNS="Full Name,Headline,Company,Location,Connections,About,Experience,Education,Skills"
# ===============================

mkdir -p "$LOG_DIR/batches" "$LOG_DIR/outputs"

status() { echo -e "[$(date +"%F %T")] $*"; }
log_file="$LOG_DIR/batch_run.log"
touch "$log_file"

# Convert Excel to CSV if needed
if [[ "$INPUT_FILE" == *.xlsx ]]; then
    status "Converting $INPUT_FILE to CSV..."
    python3 -c "
import sys, polars as pl
df = pl.read_excel(sys.argv[1])
df.write_csv(sys.argv[2])
" "$INPUT_FILE" "$LOG_DIR/input.csv"
    CSV_FILE="$LOG_DIR/input.csv"
elif [[ "$INPUT_FILE" == *.csv ]]; then
    CSV_FILE="$INPUT_FILE"
else
    status "Input must be .xlsx or .csv"
    exit 1
fi

# Split CSV into batches (assumes 1st column is LinkedIn URL)
status "Splitting CSV into batches of $BATCH_SIZE..."
split -l $BATCH_SIZE -d --additional-suffix=.csv "$CSV_FILE" "$LOG_DIR/batches/batch_"

total_batches=$(ls "$LOG_DIR/batches" | wc -l)
status "Total batches: $total_batches"

# Progress tracking file
PROGRESS_FILE="$LOG_DIR/batch_progress.txt"
touch "$PROGRESS_FILE"

for batch_csv in "$LOG_DIR"/batches/*.csv; do
    batch_id=$(basename "$batch_csv" .csv)
    batch_json="$LOG_DIR/batches/${batch_id}.json"
    batch_output="$LOG_DIR/outputs/${batch_id}_output.json"
    batch_xlsx="$LOG_DIR/outputs/${batch_id}_output.xlsx"

    # Skip if already processed
    if grep -q "^$batch_id$" "$PROGRESS_FILE"; then
        status "Skipping $batch_id (already completed)" | tee -a "$log_file"
        continue
    fi

    # Prepare per-batch input.json (edit inputPath/inputType only)
    jq ".inputType=\"csv\" | .inputPath=\"$batch_csv\"" "$INPUT_JSON_TEMPLATE" > "$batch_json"

    # Retry up to MAX_RETRIES times
    for try in $(seq 1 $MAX_RETRIES); do
        status "Processing $batch_id (try $try)..." | tee -a "$log_file"
        if python3 -m src.cli "$batch_json" > "$batch_output" 2>>"$log_file"; then
            # Convert JSON to Excel
            status "Converting $batch_id output to Excel..." | tee -a "$log_file"
            python3 -c "
import sys, polars as pl, json, pandas as pd
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
            status "Batch $batch_id completed." | tee -a "$log_file"
            break
        else
            status "Batch $batch_id failed on try $try." | tee -a "$log_file"
            sleep $((try*10))
        fi
    done

    # If not successful after retries, mark as failed
    if ! grep -q "^$batch_id$" "$PROGRESS_FILE"; then
        status "Batch $batch_id failed after $MAX_RETRIES tries, aborting." | tee -a "$log_file"
        exit 1
    fi
done

# Merge all Excel outputs
status "Merging all batch Excel files to $FINAL_OUTPUT..."
python3 -c "
import glob, pandas as pd, os
files = sorted(glob.glob('$LOG_DIR/outputs/*_output.xlsx'))
dfs = [pd.read_excel(f) for f in files if os.path.getsize(f) > 0]
if dfs:
    pd.concat(dfs, ignore_index=True).to_excel('$FINAL_OUTPUT', index=False)
else:
    print('No results to merge.')
"

status "All batches complete. Final output: $FINAL_OUTPUT"