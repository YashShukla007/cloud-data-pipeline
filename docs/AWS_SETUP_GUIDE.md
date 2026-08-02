# ☁️ AWS Setup Guide — Step by Step
# Every single click explained for a beginner

---

## PART 1 — Create Your AWS Account (Free)

1. Go to https://aws.amazon.com/free
2. Click "Create a Free Account"
3. Enter your email and a password
4. Choose "Personal" account type
5. Enter your card details (you will NOT be charged — Free Tier covers everything we need)
6. Verify your phone number
7. Choose "Basic Support" (free)
8. Done — you're in the AWS Console!

---

## PART 2 — Create Two S3 Buckets

Think of S3 buckets like folders in the cloud.
We need TWO:
- **Input bucket**  → where you DROP your messy CSV
- **Output bucket** → where Lambda saves the CLEANED CSV

### Create Input Bucket:
1. Go to AWS Console → search "S3" in top search bar → click S3
2. Click orange "Create bucket" button
3. Bucket name: `yash-pipeline-input` (must be globally unique — add your name/number if taken)
4. Region: Choose "Asia Pacific (Mumbai)" → ap-south-1  (closest to India)
5. Leave everything else as default
6. Click "Create bucket"

### Create Output Bucket:
1. Click "Create bucket" again
2. Bucket name: `yash-pipeline-output`
3. Same region: ap-south-1
4. Click "Create bucket"

You now have two buckets. ✅

---

## PART 3 — Create the IAM Role for Lambda

IAM Role = a permission card that says "Lambda is allowed to read/write S3 and write logs"
WITHOUT this, Lambda can't touch S3 at all.

1. AWS Console → search "IAM" → click IAM
2. Left sidebar → click "Roles"
3. Click "Create role"
4. Trusted entity type: "AWS service"
5. Use case: Select "Lambda" → click Next
6. Search and add these 2 policies (tick both):
   - `AmazonS3FullAccess`       → lets Lambda read/write S3
   - `CloudWatchLogsFullAccess` → lets Lambda write logs
7. Click Next
8. Role name: `yash-lambda-s3-role`
9. Click "Create role"

Done — Lambda now has permission to use S3 and CloudWatch. ✅

---

## PART 4 — Create the Lambda Function

1. AWS Console → search "Lambda" → click Lambda
2. Click "Create function"
3. Choose "Author from scratch"
4. Function name: `cloud-data-pipeline`
5. Runtime: `Python 3.12`
6. Architecture: x86_64
7. Permissions → "Use an existing role" → select `yash-lambda-s3-role`
8. Click "Create function"

### Upload your code:
1. You'll see a code editor. Delete all existing code.
2. Copy-paste the ENTIRE content of `lambda/lambda_function.py` into the editor
3. Update line: `OUTPUT_BUCKET = "yash-pipeline-output"` (make sure name matches exactly)
4. Click "Deploy" (orange button)

### Add Pandas layer (Lambda doesn't have Pandas by default):
1. Scroll down to "Layers" section → click "Add a layer"
2. Choose "AWS layers"
3. Select "AWSSDKPandas-Python312"
4. Choose the latest version
5. Click "Add"

### Increase timeout (default 3 seconds is too short):
1. Click "Configuration" tab → "General configuration" → Edit
2. Timeout: change to `1 min 0 sec`
3. Memory: change to `256 MB`
4. Save

Done — Lambda function is ready. ✅

---

## PART 5 — Add S3 Trigger

This is what makes S3 automatically call Lambda when you upload a file.

1. In your Lambda function page → click "Add trigger"
2. Select "S3"
3. Bucket: `yash-pipeline-input`
4. Event types: `PUT` (fires when a file is uploaded)
5. Suffix: `.csv` (only trigger for CSV files)
6. Tick the acknowledgment checkbox
7. Click "Add"

Now whenever you upload a .csv to `yash-pipeline-input` → Lambda runs automatically! ✅

---

## PART 6 — TEST IT!

1. Go to S3 → click `yash-pipeline-input`
2. Click "Upload" → "Add files"
3. Upload the file: `sample_data/students_messy.csv`
4. Click "Upload"

### Check it worked:
1. Go to S3 → `yash-pipeline-output`
2. You should see a `cleaned/` folder with your cleaned CSV inside!
3. Download it and open in Excel — it'll be clean!

### Check the logs:
1. Go to Lambda → your function → "Monitor" tab → "View CloudWatch logs"
2. Click the latest log stream
3. You'll see all the print() logs from your function!

---

## PART 7 — What to show in the Interview

1. Open AWS Console → show the two S3 buckets
2. Show the Lambda function code
3. Upload a CSV live → show it triggers Lambda
4. Open CloudWatch → show the logs
5. Open output bucket → show the cleaned file
6. Talk through the IAM role and why it's needed

This takes about 2 minutes and looks incredibly impressive.

---

## TROUBLESHOOTING

| Problem | Fix |
|---------|-----|
| Lambda says "Access Denied" | Check IAM role has S3FullAccess |
| Lambda times out | Increase timeout to 1 minute in Configuration |
| "No module named pandas" | Add the AWSSDKPandas layer (Part 4) |
| Output bucket is empty | Check the OUTPUT_BUCKET variable name matches exactly |
| Trigger not firing | Make sure suffix is `.csv` and event type is `PUT` |
