# TeachMeWrite Incident Response Runbook

## Alert: 5xx Error Detected
**Trigger:** GCP Cloud Monitoring fires when the rate of 5xx errors on `/feedback` is > 0/s for 60 seconds.

### Step 1: Acknowledge and Triage
1. Check the Cloud Run Logs: Link to GCP Console.
2. Look for `Anthropic API Error`, `ValidationError`, or `HTTP 429`.

### Step 2: Common Failures & Fixes
- **401/403 API Key Error:** The Anthropic API key has expired or was rotated. Update the key in GCP Secret Manager and redeploy the latest revision.
- **429 Rate Limit:** Cloud Run is receiving too many requests. Check the rate limiter logs. Increase `TMW_RATE_LIMIT_PER_MIN` if legitimate traffic.
- **502/500 Error:** Check for SyntaxErrors in `main.py` or breaking changes in the `anthropic` SDK. Rollback to the previous stable revision.

### Step 3: Rollback
If the error cannot be resolved immediately, rollback to the last known good revision:
`gcloud run services update-traffic teachmewrite-ai --to-revisions=LATEST=0,PREVIOUS=100 --region asia-south1`
