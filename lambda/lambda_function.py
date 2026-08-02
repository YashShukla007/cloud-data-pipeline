"""
Cloud Data Pipeline - AWS Lambda Function
==========================================
This is the HEART of the project.

WHAT HAPPENS:
1. Someone uploads a CSV/JSON file to S3 (input bucket)
2. S3 automatically calls THIS function
3. We clean the data using Pandas
4. Save cleaned file to another S3 bucket (output bucket)
5. Log everything to CloudWatch (automatically via print())

CONCEPTS USED:
- boto3     : AWS SDK for Python (lets Python talk to AWS)
- pandas    : Data cleaning library
- S3 event  : The trigger that calls this function
- CloudWatch: AWS logging (every print() goes here automatically)
"""

import boto3        # AWS SDK - lets us talk to S3
import pandas as pd # Data manipulation
import io           # For handling file content in memory (no disk needed)
import json         # For the return response
import logging      # Better logging than print()
from datetime import datetime

# Set up logger - this sends logs to CloudWatch automatically
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create S3 client - this is how we talk to S3
# boto3 automatically uses the IAM Role permissions attached to Lambda
s3 = boto3.client('s3')

# ── CONFIGURATION ─────────────────────────────────────────────────────
# Change this to your actual output bucket name
OUTPUT_BUCKET = "yash-pipeline-output"   # <-- UPDATE THIS


def lambda_handler(event, context):
    """
    This is the ENTRY POINT - AWS calls this function automatically.

    Parameters:
    -----------
    event   : dict - Contains info about WHAT triggered this function
                     (which file was uploaded, to which bucket, etc.)
    context : object - Contains info about the Lambda execution environment
                       (how much memory, time remaining, etc.)

    Returns:
    --------
    dict with statusCode and body (standard Lambda response format)
    """

    logger.info("=" * 60)
    logger.info("Pipeline Started")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")

    try:
        # ── STEP 1: EXTRACT info from the S3 event ───────────────────
        # When S3 triggers Lambda, it sends an 'event' dict like:
        # { "Records": [ { "s3": { "bucket": {...}, "object": {...} } } ] }
        #
        # We extract which bucket and file triggered this

        record = event['Records'][0]                          # First record
        source_bucket = record['s3']['bucket']['name']        # e.g. "yash-pipeline-input"
        file_key = record['s3']['object']['key']              # e.g. "students.csv"

        logger.info(f"Source Bucket : {source_bucket}")
        logger.info(f"File          : {file_key}")

        # ── STEP 2: DOWNLOAD the file from S3 into memory ────────────
        # We don't save to disk - Lambda has limited /tmp storage
        # Instead we read it directly into a Python string using io.StringIO

        logger.info("Downloading file from S3...")
        response = s3.get_object(Bucket=source_bucket, Key=file_key)
        file_content = response['Body'].read().decode('utf-8')

        logger.info(f"File size: {len(file_content)} bytes")

        # ── STEP 3: LOAD into Pandas DataFrame ───────────────────────
        # Detect file type from extension and load accordingly

        if file_key.endswith('.csv'):
            df = pd.read_csv(io.StringIO(file_content))
            logger.info("Loaded as CSV")

        elif file_key.endswith('.json'):
            df = pd.read_json(io.StringIO(file_content))
            logger.info("Loaded as JSON")

        else:
            raise ValueError(f"Unsupported file type: {file_key}. Only CSV and JSON supported.")

        rows_before = len(df)
        cols_before = list(df.columns)
        logger.info(f"Shape before cleaning: {df.shape}")
        logger.info(f"Columns: {cols_before}")

        # ── STEP 4: TRANSFORM - Clean the data ───────────────────────
        # This is the main data engineering work

        df, report = clean_data(df)

        rows_after = len(df)
        logger.info(f"Shape after cleaning : {df.shape}")

        # ── STEP 5: LOAD - Save cleaned file to output S3 bucket ─────
        # We construct the output path: cleaned/original_filename
        # e.g. input: "students.csv" → output: "cleaned/students_cleaned.csv"

        base_name = file_key.replace('.csv', '').replace('.json', '')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_key = f"cleaned/{base_name}_cleaned_{timestamp}.csv"

        logger.info(f"Saving to: s3://{OUTPUT_BUCKET}/{output_key}")

        # Convert DataFrame back to CSV string and upload
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)

        s3.put_object(
            Bucket=OUTPUT_BUCKET,
            Key=output_key,
            Body=csv_buffer.getvalue(),
            ContentType='text/csv'
        )

        logger.info("File saved successfully!")

        # ── STEP 6: Save the cleaning REPORT as JSON ─────────────────
        report['source_file'] = file_key
        report['output_file'] = output_key
        report['rows_before'] = rows_before
        report['rows_after'] = rows_after
        report['rows_removed'] = rows_before - rows_after
        report['timestamp'] = datetime.now().isoformat()

        report_key = f"reports/{base_name}_report_{timestamp}.json"
        s3.put_object(
            Bucket=OUTPUT_BUCKET,
            Key=report_key,
            Body=json.dumps(report, indent=2),
            ContentType='application/json'
        )

        logger.info(f"Report saved to: s3://{OUTPUT_BUCKET}/{report_key}")
        logger.info("=" * 60)
        logger.info("Pipeline Completed Successfully!")
        logger.info(f"Rows processed : {rows_before}")
        logger.info(f"Rows kept      : {rows_after}")
        logger.info(f"Rows removed   : {rows_before - rows_after}")
        logger.info("=" * 60)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Pipeline completed successfully',
                'source': f"s3://{source_bucket}/{file_key}",
                'output': f"s3://{OUTPUT_BUCKET}/{output_key}",
                'report': f"s3://{OUTPUT_BUCKET}/{report_key}",
                'rows_before': rows_before,
                'rows_after': rows_after
            })
        }

    except Exception as e:
        logger.error(f"Pipeline FAILED: {str(e)}")
        raise e  # Re-raise so Lambda marks execution as failed


def clean_data(df):
    """
    All data cleaning logic in one place.

    WHY A SEPARATE FUNCTION?
    - Easier to test locally (just call clean_data() without AWS)
    - Cleaner code, single responsibility
    - Easy to add/remove cleaning steps

    Returns:
    --------
    df     : cleaned DataFrame
    report : dict describing what was cleaned
    """

    report = {}

    # 1. Strip whitespace from column names
    # e.g. " Name " → "name", "Age " → "age"
    original_cols = list(df.columns)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    report['columns_renamed'] = {o: n for o, n in zip(original_cols, df.columns) if o != n}

    # 2. Strip whitespace from string values
    # e.g. "  John  " → "John"
    # Note: re-detect str_cols AFTER renaming columns
    str_cols = df.select_dtypes(include=['object']).columns
    for col in str_cols:
        df[col] = df[col].str.strip()

    # 3. Remove duplicate rows
    dupes_before = df.duplicated().sum()
    df.drop_duplicates(inplace=True)
    report['duplicates_removed'] = int(dupes_before)

    # 4. Remove rows where ALL values are missing (do this BEFORE filling)
    df.dropna(how='all', inplace=True)

    # 5. Handle missing values
    missing_before = df.isnull().sum().to_dict()
    report['missing_values_per_column'] = {k: int(v) for k, v in missing_before.items() if v > 0}

    # For numeric columns: fill with median (robust to outliers)
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        if df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)

    # For text columns: fill with 'Unknown'
    str_cols = df.select_dtypes(include=['object']).columns
    for col in str_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna('Unknown')

    # 6. Reset index after all removals
    df.reset_index(drop=True, inplace=True)

    report['cleaning_steps'] = [
        "Stripped whitespace from column names and standardized to lowercase",
        "Stripped whitespace from string values",
        f"Removed {report['duplicates_removed']} duplicate rows",
        "Filled missing numeric values with column median",
        "Filled missing text values with 'Unknown'",
        "Removed fully empty rows",
    ]

    return df, report
