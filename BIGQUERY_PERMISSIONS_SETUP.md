# BigQuery Permission Setup Commands

## 🎯 CURRENT STATUS
- ✅ BigQuery client can connect to ethhackathon project
- ✅ Dataset `onchain_data` already exists in ethhackathon project
- ❌ Service account lacks read/write permissions to the dataset
- ❌ Cannot create tables or insert data

## Option 1: Command Line (requires Owner/Admin permissions)

You'll need to run these commands as a user with Owner or IAM Admin permissions on the ethhackathon project:

```bash
# First, authenticate as your main account (not the service account)
gcloud auth login

# Set the project
gcloud config set project ethhackathon

# Grant BigQuery Data Editor role (allows create/read/update/delete on datasets and tables)
gcloud projects add-iam-policy-binding ethhackathon
    --member="serviceAccount:infra-automation@ethhackathon.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"

# Grant BigQuery Job User role (allows running queries and jobs)
gcloud projects add-iam-policy-binding ethhackathon \
    --member="serviceAccount:infra-automation@ethhackathon.iam.gserviceaccount.com" \
    --role="roles/bigquery.jobUser"

# Grant BigQuery Data Owner role (full control over datasets)
gcloud projects add-iam-policy-binding ethhackathon \
    --member="serviceAccount:infra-automation@ethhackathon.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataOwner"

# Optional: Grant BigQuery Admin (full BigQuery permissions)
gcloud projects add-iam-policy-binding ethhackathon \
    --member="serviceAccount:infra-automation@ethhackathon.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"
```

## Option 2: Google Cloud Console

1. Go to https://console.cloud.google.com/iam-admin/iam?project=ethhackathon
2. Find the service account: `infra-automation@ethhackathon.iam.gserviceaccount.com`
3. Click the pencil icon to edit
4. Add these roles:
   - BigQuery Data Editor
   - BigQuery Job User
   - BigQuery Data Owner (or BigQuery Admin for full access)

## Option 3: Quick Test Commands

After granting permissions, test with:

```bash
# Test dataset creation
bq mk --project_id=ethhackathon --dataset onchain_data

# Test table creation
bq mk --project_id=ethhackathon --table onchain_data.raw_data \
    transaction_hash:STRING,block_number:INTEGER,from_address:STRING,to_address:STRING,value:FLOAT,gas_used:INTEGER,timestamp:TIMESTAMP

# Test data insertion
echo '{"transaction_hash":"0x123","block_number":12345,"from_address":"0xabc","to_address":"0xdef","value":1.5,"gas_used":21000,"timestamp":"2024-01-01T00:00:00Z"}' | \
bq insert --project_id=ethhackathon onchain_data.raw_data
```

## Current Issue

The service account `infra-automation@ethhackathon.iam.gserviceaccount.com` currently lacks:
- BigQuery dataset creation permissions
- BigQuery data manipulation permissions
- Cloud Resource Manager API access (for project-level operations)

This is preventing our E2E tests from creating the required BigQuery infrastructure.
