"""
Local Test Runner
==================
Run this on YOUR LAPTOP to test the pipeline WITHOUT needing AWS.

This simulates exactly what Lambda does, but:
- Instead of downloading from S3, it reads a local file
- Instead of uploading to S3, it saves to a local folder
- All logs print to your terminal instead of CloudWatch

HOW TO RUN:
    python local_test/run_local.py

WHAT YOU'LL SEE:
- Step-by-step logs exactly like CloudWatch would show
- Cleaned CSV saved in local_test/output/
- Report JSON saved in local_test/output/
"""

import pandas as pd
import io
import json
import os
import sys
from datetime import datetime

# Add parent directory to path so we can import lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda'))

# Import our cleaning function directly
from lambda_function import clean_data

# ── CONFIGURATION ─────────────────────────────────────────────────────
INPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'sample_data', 'students_messy.csv')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_pipeline_locally(input_file):
    """
    Simulates the full Lambda pipeline locally.
    Same logic as lambda_function.py but reads/writes local files.
    """

    print("=" * 60)
    print("LOCAL PIPELINE TEST")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)

    # ── STEP 1: Read local file ───────────────────────────────────────
    print(f"\n[STEP 1] Reading file: {input_file}")

    if not os.path.exists(input_file):
        print(f"ERROR: File not found: {input_file}")
        print("Make sure sample_data/students_messy.csv exists!")
        return

    with open(input_file, 'r') as f:
        file_content = f.read()

    print(f"  File size: {len(file_content)} bytes")

    # ── STEP 2: Load into Pandas ──────────────────────────────────────
    print("\n[STEP 2] Loading into Pandas DataFrame...")

    if input_file.endswith('.csv'):
        df = pd.read_csv(io.StringIO(file_content))
    elif input_file.endswith('.json'):
        df = pd.read_json(io.StringIO(file_content))

    rows_before = len(df)
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    print("\n  RAW DATA (first 5 rows):")
    print(df.head().to_string())

    # ── STEP 3: Clean the data ────────────────────────────────────────
    print("\n[STEP 3] Cleaning data...")

    df_cleaned, report = clean_data(df.copy())

    rows_after = len(df_cleaned)

    print(f"  Duplicates removed    : {report['duplicates_removed']}")
    print(f"  Columns renamed       : {report['columns_renamed']}")
    print(f"  Missing values found  : {report['missing_values_per_column']}")
    print(f"  Rows before cleaning  : {rows_before}")
    print(f"  Rows after cleaning   : {rows_after}")
    print(f"  Rows removed          : {rows_before - rows_after}")

    print("\n  CLEANED DATA (first 5 rows):")
    print(df_cleaned.head().to_string())

    # ── STEP 4: Save cleaned CSV ──────────────────────────────────────
    print("\n[STEP 4] Saving cleaned file...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.basename(input_file).replace('.csv', '').replace('.json', '')
    output_csv = os.path.join(OUTPUT_DIR, f"{base_name}_cleaned_{timestamp}.csv")

    df_cleaned.to_csv(output_csv, index=False)
    print(f"  Saved to: {output_csv}")

    # ── STEP 5: Save cleaning report ─────────────────────────────────
    print("\n[STEP 5] Saving cleaning report...")

    report['source_file'] = input_file
    report['output_file'] = output_csv
    report['rows_before'] = rows_before
    report['rows_after'] = rows_after
    report['rows_removed'] = rows_before - rows_after
    report['timestamp'] = datetime.now().isoformat()

    output_report = os.path.join(OUTPUT_DIR, f"{base_name}_report_{timestamp}.json")
    with open(output_report, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"  Saved to: {output_report}")

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"  Input  : {input_file}")
    print(f"  Output : {output_csv}")
    print(f"  Report : {output_report}")
    print("=" * 60)


if __name__ == "__main__":
    # Allow passing a custom file path as argument
    # Usage: python run_local.py path/to/myfile.csv
    file_to_test = sys.argv[1] if len(sys.argv) > 1 else INPUT_FILE
    run_pipeline_locally(file_to_test)
