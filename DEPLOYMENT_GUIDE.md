# 🚀 Resume Builder - Deployment Guide

This guide covers multiple deployment options for your AI-powered Resume Builder application.

---

## 📋 Table of Contents

1. [Local Deployment](#local-deployment)
2. [Streamlit Cloud (Easiest - Free)](#streamlit-cloud-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Platforms](#cloud-platform-deployment)
5. [Security Best Practices](#security-best-practices)

---

## 🏠 Local Deployment

### Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key

# 3. Run the Streamlit app
streamlit run app.py

# 4. Open browser to http://localhost:8501
```

### Command Line Usage

```bash
# Parse and analyze only
python main.py

# With semantic matching (RAG)
python main.py --rag

# With LLM optimization
python main.py --rag --generate

# Interactive chat mode
python main.py --chat
```

---

## ☁️ Streamlit Cloud Deployment (Recommended)

**FREE for public apps | Easiest deployment**

### Steps:

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/Resume_Builder.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Main file: `app.py`
   - Click "Deploy"

3. **Add API Keys (Secrets)**
   - In your app dashboard, go to "Settings" → "Secrets"
   - Add your secrets:
   ```toml
   OPENAI_API_KEY = "sk-proj-..."
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```

4. **Your app is live!**
   - URL: `https://your-app-name.streamlit.app`
   - Auto-deploys on git push

### Pros:
✅ Free for public apps
✅ Auto SSL/HTTPS
✅ No server management
✅ Auto-scaling
✅ CI/CD built-in

### Cons:
❌ Public apps only (or paid plan)
❌ Resource limits (1GB RAM free tier)

---

## 🐳 Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model (if needed)
# RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/vector_store output

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  resume-builder:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./data:/app/data
      - ./output:/app/output
    restart: unless-stopped
```

### Build and Run

```bash
# Build image
docker build -t resume-builder .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🌐 Cloud Platform Deployment

### AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p docker resume-builder

# Create environment
eb create resume-builder-env

# Deploy
eb deploy

# Open app
eb open
```

**Cost:** ~$25-50/month (t3.small instance)

---

### Google Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/resume-builder

# Deploy
gcloud run deploy resume-builder \
  --image gcr.io/PROJECT_ID/resume-builder \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY

# Get URL
gcloud run services describe resume-builder --region us-central1
```

**Cost:** Pay per request, ~$5-20/month for low-medium traffic

---

### Azure App Service

```bash
# Login
az login

# Create resource group
az group create --name resume-builder-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name resume-builder-plan \
  --resource-group resume-builder-rg \
  --is-linux \
  --sku B1

# Create web app
az webapp create \
  --resource-group resume-builder-rg \
  --plan resume-builder-plan \
  --name resume-builder-app \
  --deployment-container-image-name resume-builder:latest

# Set environment variables
az webapp config appsettings set \
  --resource-group resume-builder-rg \
  --name resume-builder-app \
  --settings OPENAI_API_KEY=$OPENAI_API_KEY
```

**Cost:** ~$13-55/month (B1-B3 tiers)

---

### Heroku

```bash
# Install Heroku CLI
brew install heroku/brew/heroku  # macOS
# or download from https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create resume-builder-app

# Add buildpack for Python
heroku buildpacks:set heroku/python

# Set environment variables
heroku config:set OPENAI_API_KEY=$OPENAI_API_KEY

# Deploy
git push heroku main

# Open app
heroku open
```

**Cost:** ~$7-25/month (Eco/Basic dynos)

---

## 🔒 Security Best Practices

### 1. Environment Variables

**Never commit `.env` to git:**

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
```

**Use secrets management:**
- Streamlit Cloud: Built-in secrets
- AWS: Secrets Manager or Parameter Store
- GCP: Secret Manager
- Azure: Key Vault
- Heroku: Config Vars

### 2. API Key Rotation

Rotate your API keys regularly:
```bash
# OpenAI: https://platform.openai.com/api-keys
# Anthropic: https://console.anthropic.com/settings/keys
```

### 3. Rate Limiting

Add rate limiting to prevent abuse:

```python
# Add to app.py
import streamlit as st
from functools import wraps
import time

def rate_limit(max_calls=10, period=60):
    """Rate limiter decorator"""
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            calls[:] = [c for c in calls if c > now - period]
            
            if len(calls) >= max_calls:
                st.error(f"Rate limit exceeded. Try again in {int(period - (now - calls[0]))}s")
                return None
            
            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### 4. Input Validation

Validate file uploads:
```python
# Add to app.py
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt']

if uploaded_file.size > MAX_FILE_SIZE:
    st.error("File too large")
elif not any(uploaded_file.name.endswith(ext) for ext in ALLOWED_EXTENSIONS):
    st.error("Invalid file type")
```

### 5. HTTPS Only

Ensure all deployments use HTTPS:
- Streamlit Cloud: Automatic
- Cloud platforms: Configure SSL certificate
- Docker: Use reverse proxy (nginx/Caddy)

---

## 📊 Monitoring & Analytics

### Add Google Analytics (Optional)

```python
# Add to app.py
import streamlit.components.v1 as components

def add_google_analytics():
    """Add Google Analytics tracking"""
    ga_code = """
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-XXXXXXXXXX');
    </script>
    """
    components.html(ga_code, height=0)
```

### Application Monitoring

**Streamlit Cloud:** Built-in metrics
**Other platforms:** Use:
- Sentry (error tracking)
- LogRocket (session replay)
- Datadog (full monitoring)

---

## 💰 Cost Comparison

| Platform | Cost/Month | Pros | Best For |
|----------|-----------|------|----------|
| **Streamlit Cloud** | FREE-$20 | Easiest, built for Streamlit | Public apps, demos |
| **Google Cloud Run** | $5-20 | Pay per use, scales to zero | Variable traffic |
| **Heroku** | $7-25 | Easy deploy, good docs | Small-medium apps |
| **AWS EB** | $25-50 | Full AWS integration | Production apps |
| **Azure App** | $13-55 | Microsoft ecosystem | Enterprise |
| **DigitalOcean** | $12-24 | Simple, predictable | Small teams |

**API Costs (OpenAI):**
- GPT-3.5-turbo: ~$0.01/resume
- GPT-4-turbo: ~$0.10/resume

---

## 🎯 Recommended Deployment Path

### For Demo/Portfolio:
1. ✅ **Streamlit Cloud** (Free, easiest)

### For Production:
1. 🐳 **Docker + Google Cloud Run** (Cost-effective, scales)
2. 🚀 **AWS Elastic Beanstalk** (Enterprise-ready)

### For Enterprise:
1. 🏢 **Azure App Service** (If using Azure ecosystem)
2. 🔧 **Kubernetes** (If you have DevOps team)

---

## 🆘 Troubleshooting

### Port already in use
```bash
# Find process using port 8501
lsof -ti:8501 | xargs kill -9

# Or use different port
streamlit run app.py --server.port=8502
```

### Memory issues
```bash
# Increase Docker memory
docker run --memory=2g resume-builder

# Or optimize embeddings
# Use smaller model in .env:
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Build fails
```bash
# Clear pip cache
pip cache purge

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📞 Support

For deployment issues:
1. Check logs: `streamlit run app.py --logger.level=debug`
2. Verify API keys: `python test_api_key.py`
3. Test locally first before deploying

---

**Ready to deploy?** Start with Streamlit Cloud for the easiest deployment experience!

