# 🧠 Every Concept Explained — Cloud Data Pipeline

---

## 1. What is ETL?

ETL = Extract → Transform → Load

It's the most fundamental concept in data engineering.

| Step | What it means | In our project |
|------|--------------|----------------|
| **Extract** | Get raw data from somewhere | Read CSV from S3 input bucket |
| **Transform** | Clean/reshape the data | Remove duplicates, fix nulls, rename columns |
| **Load** | Save to destination | Write clean CSV to S3 output bucket |

Every data pipeline in the world — at Google, Amazon, banks — is some form of ETL.

**Interview answer:**
> "ETL stands for Extract, Transform, Load. In my project, I extract raw CSV files from an S3 bucket, transform them by removing duplicates, handling missing values, and standardizing column names using Pandas, then load the cleaned output back to a separate S3 bucket."

---

## 2. What is AWS S3?

S3 = Simple Storage Service

It's basically a hard drive in the cloud. You can store ANY file — CSV, images, videos, JSON.

**Key terms:**
- **Bucket** = like a folder. Has a globally unique name.
- **Object** = any file stored in the bucket
- **Key** = the file's path/name inside the bucket (e.g., `cleaned/students.csv`)

**Why S3 and not your laptop's hard drive?**
- Available 24/7 from anywhere
- Scales to petabytes
- Other AWS services (Lambda) can read/write it directly
- 99.999999999% durability (11 nines!)

**Interview answer:**
> "S3 is AWS's object storage service. I used two S3 buckets — one as the landing zone for raw input files, and one to store the cleaned outputs and pipeline reports. S3 acts as the glue between the file upload and the Lambda trigger."

---

## 3. What is AWS Lambda?

Lambda is a service that runs YOUR code without you needing to manage any server.

**Traditional approach (without Lambda):**
- Buy/rent a server
- Install Python, Pandas, etc.
- Keep server running 24/7 (costs money even when idle)
- Manually run your script

**With Lambda:**
- Upload your Python code
- Define WHEN it should run (e.g., when a file lands in S3)
- AWS runs it automatically
- You pay ONLY for the time it runs (first 1 million calls/month are FREE)

**Key concepts:**
- **Handler** = `lambda_handler(event, context)` — the entry point AWS calls
- **Event** = the dict AWS sends describing what triggered the function
- **Context** = info about the execution (time remaining, memory, etc.)
- **Timeout** = max time Lambda will run (we set 1 minute)
- **Memory** = RAM given to your function (we set 256 MB)

**Interview answer:**
> "Lambda is AWS's serverless compute service. I wrote the ETL logic as a Lambda function in Python. It gets triggered automatically by S3 when a new file is uploaded — no server management needed. The function downloads the file, cleans it with Pandas, and saves the output back to S3. The whole execution takes a few seconds and costs essentially nothing."

---

## 4. What is a Trigger?

A trigger = a rule that says "when X happens, run Y".

In our project:
- **X** = a CSV file is uploaded to `yash-pipeline-input` S3 bucket
- **Y** = Lambda function `cloud-data-pipeline` runs

This is called **event-driven architecture** — code runs in RESPONSE to events, not on a schedule.

**Interview answer:**
> "I configured an S3 event notification as the trigger. When any .csv file is uploaded to the input bucket, S3 sends an event to Lambda containing the bucket name and file key. Lambda then processes that specific file. This makes the pipeline fully automated — no cron jobs or manual runs needed."

---

## 5. What is IAM?

IAM = Identity and Access Management

It's AWS's permission system. Every service needs explicit permission to talk to another service.

**Without IAM:** Lambda can't read S3. Can't write logs. Can't do anything.
**With IAM:** We create a ROLE that says "Lambda is allowed to: read S3, write S3, write CloudWatch logs."

**Key terms:**
- **Role** = a set of permissions assigned to an AWS service
- **Policy** = a document defining what is allowed (e.g., AmazonS3FullAccess)

**Interview answer:**
> "I created an IAM role called 'yash-lambda-s3-role' and attached two policies — AmazonS3FullAccess and CloudWatchLogsFullAccess. This role is assigned to the Lambda function, giving it exactly the permissions it needs to read from the input bucket, write to the output bucket, and send logs to CloudWatch. IAM follows the principle of least privilege — only grant what's needed."

---

## 6. What is CloudWatch?

CloudWatch = AWS's logging and monitoring service.

When your Lambda function runs, every `print()` or `logger.info()` statement gets saved to CloudWatch automatically.

**What you can see in CloudWatch:**
- When the function ran
- How long it took
- How many rows were processed
- Any errors that occurred

**Why it matters:**
- In production, you can't "watch" your code run
- CloudWatch lets you debug issues after the fact
- You can set up alerts (e.g., email me if pipeline fails)

**Interview answer:**
> "I used Python's logging module in Lambda, which automatically sends all logs to CloudWatch. This lets me monitor every pipeline run — how many rows were processed, what was cleaned, how long it took, and any errors. In a production environment, you'd set up CloudWatch alarms to alert on failures."

---

## 7. What is boto3?

boto3 = the official AWS SDK (library) for Python.

It lets your Python code talk to ANY AWS service.

```python
import boto3

s3 = boto3.client('s3')

# Download a file from S3
response = s3.get_object(Bucket='my-bucket', Key='myfile.csv')

# Upload a file to S3
s3.put_object(Bucket='my-bucket', Key='output.csv', Body=csv_data)
```

**Interview answer:**
> "I used boto3, the AWS SDK for Python, to interact with S3 programmatically — downloading the input file into memory and uploading the cleaned output. boto3 automatically uses the IAM role's credentials, so there's no hardcoded API keys."

---

## 8. Why io.StringIO instead of saving to disk?

Lambda has very limited disk space (/tmp, max 512 MB).
For large files, reading into memory is faster and safer.

```python
# WRONG - saves to disk
with open('/tmp/file.csv', 'w') as f:
    df.to_csv(f)

# RIGHT - stays in memory
buffer = io.StringIO()
df.to_csv(buffer)
data = buffer.getvalue()  # this is the CSV as a string, ready to upload
```

**Interview answer:**
> "I used io.StringIO to handle file content entirely in memory, avoiding disk I/O. This is a best practice for Lambda because disk access is slower and Lambda's /tmp storage is limited. The file goes: S3 → memory (StringIO) → Pandas → memory (StringIO) → S3."

---

## 9. What is Serverless?

Serverless doesn't mean "no server" — it means YOU don't manage the server.

| Traditional | Serverless (Lambda) |
|-------------|---------------------|
| Rent a VM/server | No server to manage |
| Pay 24/7 | Pay only when code runs |
| You install Python, patches, etc. | AWS handles everything |
| Scales manually | Scales automatically |

**Interview answer:**
> "The pipeline is serverless — I'm using AWS Lambda which means I don't provision or manage any servers. AWS automatically scales it if 100 files are uploaded simultaneously. I only pay for actual compute time, which for this pipeline is essentially free under the AWS Free Tier."

---

## 10. Key Numbers to Remember

| Thing | Value | Why it matters |
|-------|-------|----------------|
| Lambda free tier | 1 million invocations/month | Our pipeline is free |
| Lambda max timeout | 15 minutes | We set 1 minute |
| Lambda memory | 128 MB – 10 GB | We use 256 MB |
| S3 free tier | 5 GB storage | More than enough |
| CloudWatch free | 5 GB logs/month | Free for our use |
