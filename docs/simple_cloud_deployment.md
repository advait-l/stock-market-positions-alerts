# Simple Cloud Deployment Guide

This document provides a step-by-step guide for the simplest cloud deployment setup for the Stock Market Positions Alerts application. This approach prioritizes simplicity while maintaining production-readiness.

## Recommended Architecture Overview

- **Backend**: Google Cloud Run (serverless containers)
- **Database**: InfluxDB Cloud (managed time-series database)
- **Frontend**: Vercel (as already planned)
- **Benefits**: 
  - No server management
  - Pay-per-use pricing
  - Automatic scaling
  - Simple CI/CD setup

## Prerequisites

1. Google Cloud Platform account
2. InfluxDB Cloud account
3. Vercel account (for frontend)
4. Docker installed locally
5. Google Cloud CLI installed

## Step 1: Database Setup (InfluxDB Cloud)

### 1.1 Create InfluxDB Cloud Account

1. Visit [https://cloud2.influxdata.com/signup](https://cloud2.influxdata.com/signup)
2. Sign up for a free account
3. Create a new organization and bucket

### 1.2 Get Database Credentials

1. Go to **Data > API Tokens**
2. Generate a new token with read/write permissions
3. Note down:
   - Organization ID
   - Bucket name
   - API Token
   - Server URL (e.g., `https://us-east-1-1.aws.cloud2.influxdata.com`)

### 1.3 Update Backend Configuration

Create or update your environment configuration in the backend to use these credentials.

## Step 2: Backend Deployment (Google Cloud Run)

### 2.1 Setup Google Cloud Project

1. **Install Google Cloud CLI** (if not already installed):
   ```bash
   # On Ubuntu/Debian
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   
   # On macOS
   brew install --cask google-cloud-sdk
   ```

2. **Initialize and authenticate**:
   ```bash
   gcloud init
   gcloud auth login
   ```

3. **Create a new project** (or use existing):
   ```bash
   gcloud projects create stock-alerts-project --name="Stock Alerts"
   gcloud config set project stock-alerts-project
   ```

4. **Enable required APIs**:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

### 2.2 Prepare Backend for Cloud Run

1. **Update requirements.txt** to include gunicorn:
   ```bash
   cd src/backend
   echo "gunicorn" >> requirements.txt
   ```

2. **Verify Dockerfile** (already exists and looks good):
   - The existing Dockerfile is already optimized for Cloud Run
   - Port 8000 is correctly exposed
   - Gunicorn with Uvicorn worker is configured

3. **Create environment variables file** (`.env.production`):
   ```bash
   # Create in src/backend/
   INFLUXDB_URL=your_influxdb_cloud_url
   INFLUXDB_TOKEN=your_influxdb_token
   INFLUXDB_ORG=your_organization_id
   INFLUXDB_BUCKET=your_bucket_name
   ENVIRONMENT=production
   ```

### 2.3 Deploy to Cloud Run

1. **Build and push container**:
   ```bash
   cd src/backend
   
   # Build the container
   gcloud builds submit --tag gcr.io/stock-alerts-project/stock-alerts-backend
   ```

2. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy stock-alerts-backend \
     --image gcr.io/stock-alerts-project/stock-alerts-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8000 \
     --set-env-vars INFLUXDB_URL=your_influxdb_cloud_url,INFLUXDB_TOKEN=your_influxdb_token,INFLUXDB_ORG=your_organization_id,INFLUXDB_BUCKET=your_bucket_name,ENVIRONMENT=production
   ```

3. **Note the service URL** that's provided after deployment (e.g., `https://stock-alerts-backend-xxx-uc.a.run.app`)

### 2.4 Set up Custom Domain (Optional)

1. **Map custom domain**:
   ```bash
   gcloud run domain-mappings create --service stock-alerts-backend --domain api.yourdomain.com --region us-central1
   ```

## Step 3: Frontend Deployment (Vercel)

### 3.1 Update Frontend Configuration

1. **Update API endpoint** in your frontend environment variables:
   ```bash
   # In src/frontend/.env.local
   NEXT_PUBLIC_API_URL=https://stock-alerts-backend-xxx-uc.a.run.app
   ```

### 3.2 Deploy to Vercel

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from frontend directory**:
   ```bash
   cd src/frontend
   vercel --prod
   ```

4. **Set environment variables in Vercel dashboard**:
   - Go to your project settings in Vercel
   - Add `NEXT_PUBLIC_API_URL` with your Cloud Run backend URL

## Step 4: CI/CD Setup (Optional but Recommended)

### 4.1 Backend CI/CD with GitHub Actions

Create `.github/workflows/deploy-backend.yml`:

```yaml
name: Deploy Backend to Cloud Run

on:
  push:
    branches: [ main ]
    paths: [ 'src/backend/**' ]

env:
  PROJECT_ID: stock-alerts-project
  SERVICE: stock-alerts-backend
  REGION: us-central1

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - id: 'auth'
      uses: 'google-github-actions/auth@v1'
      with:
        credentials_json: '${‌{ secrets.GCP_SA_KEY }}'
    
    - name: 'Set up Cloud SDK'
      uses: 'google-github-actions/setup-gcloud@v1'
    
    - name: 'Build and Push Container'
      run: |-
        cd src/backend
        gcloud builds submit --tag "gcr.io/$PROJECT_ID/$SERVICE:$GITHUB_SHA"
    
    - name: 'Deploy to Cloud Run'
      run: |-
        gcloud run deploy "$SERVICE" \
          --quiet \
          --region "$REGION" \
          --image "gcr.io/$PROJECT_ID/$SERVICE:$GITHUB_SHA" \
          --platform "managed" \
          --allow-unauthenticated
```

### 4.2 Set up GitHub Secrets

1. Create a GCP service account with Cloud Run Admin and Storage Admin roles
2. Download the JSON key
3. Add it as `GCP_SA_KEY` secret in GitHub repository settings

## Step 5: Monitoring and Logging

### 5.1 Enable Cloud Run Logging

Logs are automatically available in Google Cloud Console under **Cloud Run > your-service > Logs**.

### 5.2 Set up Alerts (Optional)

1. Go to **Monitoring > Alerting** in Google Cloud Console
2. Create alerts for:
   - High error rates
   - High latency
   - Service downtime

## Cost Estimation

**Monthly costs for moderate usage:**
- **Google Cloud Run**: $0-20 (first 2 million requests free)
- **InfluxDB Cloud**: $0-45 (free tier available, then ~$45/month)
- **Vercel**: $0 (free for personal projects)
- **Total**: $0-65/month

## Security Considerations

1. **Environment Variables**: Store sensitive data in Cloud Run environment variables
2. **CORS**: Update CORS origins in backend to include your Vercel domain
3. **API Keys**: Use Google Secret Manager for sensitive credentials (advanced)

## Troubleshooting

### Common Issues

1. **Container fails to start**:
   - Check logs in Cloud Run console
   - Verify port 8000 is correctly configured
   - Ensure all dependencies are in requirements.txt

2. **CORS errors**:
   - Update CORS origins in `src/backend/app/main.py`
   - Add your Vercel domain to allowed origins

3. **Database connection issues**:
   - Verify InfluxDB credentials
   - Check if InfluxDB Cloud instance is running
   - Test connection locally first

### Testing Deployment

1. **Test backend endpoint**:
   ```bash
   curl https://your-cloud-run-url/
   ```

2. **Test API endpoints**:
   ```bash
   curl https://your-cloud-run-url/api/stocks
   ```

## Next Steps

1. Set up monitoring and alerting
2. Configure custom domains
3. Implement proper logging
4. Set up backup strategies for InfluxDB
5. Consider implementing API rate limiting
6. Add health check endpoints

This deployment setup provides a balance of simplicity and production-readiness, allowing you to focus on developing features rather than managing infrastructure. 