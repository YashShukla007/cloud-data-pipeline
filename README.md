# ☁️ Cloud Data Pipeline — AWS S3 + Lambda + Python

A serverless ETL pipeline that automatically cleans CSV/JSON data using AWS Lambda, triggered by S3 file uploads.

## 🏗️ Architecture

```
You upload CSV
      ↓
[S3 Input Bucket]  →  triggers  →  [AWS Lambda (Python)]
                                          ↓
                                    Cleans data with Pandas
                                    (removes duplicates,
                                     fixes missing values,
                                     standardizes columns)
                                          ↓
                              [S3 Output Bucket]    [CloudWatch Logs]
                              cleaned CSV + report   execution logs
```

## 📁 Project Structure

```
cloud-data-pipeline/
│
├── lambda/
│   └── lambda_function.py      # Main Lambda code — deploy this to AWS
│
├── local_test/
│   ├── run_local.py            # Test pipeline on your laptop (no AWS needed)
│   └── test_pipeline.py        # Unit tests with pytest
│
├── sample_data/
│   └── students_messy.csv      # Sample messy data to test with
│
├── docs/
│   ├── AWS_SETUP_GUIDE.md      # Step-by-step AWS setup (every click explained)
│   └── CONCEPTS_EXPLAINED.md  # Every concept explained in detail
│
└── requirements.txt            # Python dependencies
```

## 🚀 Quick Start (Local — No AWS needed)

```bash
# 1. Clone the repo
git clone https://github.com/YashShukla007/cloud-data-pipeline.git
cd cloud-data-pipeline

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the pipeline locally
python local_test/run_local.py

# 4. Run unit tests
pip install pytest
pytest local_test/test_pipeline.py -v
```

## ☁️ Deploy to AWS

Follow the complete step-by-step guide: [AWS_SETUP_GUIDE.md](docs/AWS_SETUP_GUIDE.md)

**Overview:**
1. Create two S3 buckets (input + output)
2. Create an IAM role with S3 + CloudWatch permissions
3. Create a Lambda function (Python 3.12) and paste `lambda_function.py`
4. Add the AWSSDKPandas layer (for Pandas support)
5. Add an S3 trigger on the input bucket
6. Upload a CSV to input bucket → cleaned file appears in output bucket!

## 🧹 What the Pipeline Cleans

| Issue | Fix Applied |
|-------|------------|
| Duplicate rows | Removed, keeping first occurrence |
| Leading/trailing spaces in column names | Stripped and lowercased |
| Leading/trailing spaces in values | Stripped |
| Missing numeric values | Filled with column median |
| Missing text values | Filled with 'Unknown' |
| Completely empty rows | Removed |

## 📊 Sample Output

**Input (messy):**
```
Name ,Age, Email , Department ,Score
John Doe,21,john@example.com,Computer Science,85
John Doe,21,john@example.com,Computer Science,85   ← duplicate
Ravi Kumar,,ravi@example.com,Mechanical,78          ← missing age
```

**Output (cleaned):**
```
name,age,email,department,score
John Doe,21,john@example.com,Computer Science,85
Ravi Kumar,21.5,ravi@example.com,Mechanical,78      ← age filled with median
```

## 🧪 Running Tests

```bash
pytest local_test/test_pipeline.py -v
```

Tests cover:
- Duplicate removal
- Column name normalization
- Whitespace stripping
- Missing numeric → median fill
- Missing text → 'Unknown' fill
- Empty row removal
- Clean data passes through unchanged

## 🛠️ Tech Stack

- **Python 3.12** — Core language
- **Pandas** — Data cleaning
- **boto3** — AWS SDK (S3 operations)
- **AWS Lambda** — Serverless compute
- **AWS S3** — Cloud file storage
- **AWS IAM** — Permissions management
- **AWS CloudWatch** — Logging & monitoring

## 📚 Learn the Concepts

All concepts (ETL, Lambda, S3, IAM, CloudWatch, boto3, serverless) explained in plain English:
[CONCEPTS_EXPLAINED.md](docs/CONCEPTS_EXPLAINED.md)

## 👤 Author

**Yash Shukla**
- LinkedIn: [Yash Shukla](https://linkedin.com/in/yashshukla)
- GitHub: [YashShukla007](https://github.com/YashShukla007)
