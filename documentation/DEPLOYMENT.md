# 🚀 Deployment Guide

This guide will help you deploy the AI Personal Finance Copilot to production.

## 📋 Pre-Deployment Checklist

- [ ] Test locally with sample data
- [ ] Add AI API key (optional but recommended)
- [ ] Update CORS settings for production domain
- [ ] Test all API endpoints
- [ ] Review security settings

## 🔧 Option 1: Deploy to Render (Recommended)

### Backend Deployment

1. **Create account** at [render.com](https://render.com)

2. **Create Web Service**
   - Connect your GitHub repository
   - Select the `backend` directory
   - Configure:
     ```
     Build Command: pip install -r requirements.txt
     Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

3. **Add Environment Variables**
   ```
   ANTHROPIC_API_KEY=your_anthropic_key
   OPENAI_API_KEY=your_openai_key
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (2-3 minutes)
   - Note your backend URL: `https://your-app.onrender.com`

### Frontend Deployment

1. **Update API URL** in `frontend/app.js`:
   ```javascript
   const API_URL = 'https://your-backend.onrender.com';
   ```

2. **Deploy to Vercel**
   - Install Vercel CLI: `npm i -g vercel`
   - Run: `cd frontend && vercel`
   - Follow prompts
   - Get URL: `https://your-app.vercel.app`

3. **Update CORS** in backend `main.py`:
   ```python
   allow_origins=["https://your-app.vercel.app"]
   ```

## 🔧 Option 2: Deploy to Railway

### Backend

1. **Create account** at [railway.app](https://railway.app)

2. **New Project from GitHub**
   - Select your repository
   - Add service from `backend` directory

3. **Configure**
   ```
   Root Directory: backend
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Add Variables**
   - Add API keys in Variables tab

5. **Deploy**
   - Automatic deployment on push
   - Get URL from settings

### Frontend

Same as Vercel above, or use Railway static site.

## 🔧 Option 3: Deploy to Heroku

### Backend

1. **Install Heroku CLI**
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Create Procfile** in backend directory:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

3. **Deploy**
   ```bash
   heroku login
   heroku create your-app-name
   git subtree push --prefix backend heroku main
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set ANTHROPIC_API_KEY=your_key
   ```

## 🔧 Option 4: Deploy to AWS/DigitalOcean

### Using Docker

1. **Create Dockerfile** in backend:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8000
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Build and Push**
   ```bash
   docker build -t finance-copilot-backend .
   docker tag finance-copilot-backend your-registry/finance-copilot
   docker push your-registry/finance-copilot
   ```

3. **Deploy to EC2/Droplet**
   ```bash
   docker pull your-registry/finance-copilot
   docker run -d -p 8000:8000 \
     -e ANTHROPIC_API_KEY=your_key \
     your-registry/finance-copilot
   ```

## 🔐 Security Best Practices

### 1. Environment Variables
Never commit API keys. Use environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('ANTHROPIC_API_KEY')
```

### 2. CORS Configuration
Update for production:
```python
allow_origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]
```

### 3. Rate Limiting
Add rate limiting to prevent abuse:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/insights")
@limiter.limit("10/minute")
async def get_insights():
    ...
```

### 4. HTTPS Only
Ensure all production traffic uses HTTPS.

### 5. Input Validation
Already implemented in the code, but review:
- File size limits
- CSV format validation
- SQL injection prevention

## 📊 Monitoring

### 1. Health Check Endpoint
Add to `main.py`:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

### 2. Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/api/upload")
async def upload_transactions(file: UploadFile):
    logger.info(f"Upload started: {file.filename}")
    # ... rest of code
```

### 3. Error Tracking
Consider integrating Sentry:
```python
import sentry_sdk

sentry_sdk.init(dsn="your-dsn")
```

## 🧪 Testing in Production

1. **Upload sample data**
   ```bash
   curl -X POST -F "file=@sample_transactions.csv" \
     https://your-api.com/api/upload
   ```

2. **Check endpoints**
   ```bash
   curl https://your-api.com/api/stats
   curl https://your-api.com/api/categories
   curl https://your-api.com/api/insights
   ```

3. **Load testing** (optional)
   ```bash
   # Install Apache Bench
   ab -n 100 -c 10 https://your-api.com/api/stats
   ```

## 🔄 CI/CD Pipeline

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Render
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
        run: |
          curl -X POST https://api.render.com/deploy/...
```

## 📈 Post-Deployment

1. **Monitor logs** for errors
2. **Test all features** with real data
3. **Set up alerts** for downtime
4. **Document your API** at `/docs` endpoint
5. **Share demo link** in your application

## 🆘 Troubleshooting

### Common Issues

**Issue**: CORS errors in browser
**Solution**: Update `allow_origins` in backend

**Issue**: 500 errors on upload
**Solution**: Check file size limits and CSV format

**Issue**: AI insights not generating
**Solution**: Verify API key is set correctly

**Issue**: Slow response times
**Solution**: Add database caching, optimize queries

## 📞 Support

For deployment issues:
1. Check application logs
2. Review error messages in browser console
3. Test API endpoints directly with curl
4. Verify environment variables are set

---

**Ready to deploy?** Pick your platform and follow the guide above!
