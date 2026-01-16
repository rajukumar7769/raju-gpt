# RAJU-GPT Deployment Guide

## 🚀 Quick Start - Hugging Face Spaces (Recommended Free Option)

**Best for**: Free hosting with 16GB RAM, perfect for your 2.2GB model

### Prerequisites
1. GitHub account
2. Hugging Face account (sign up at https://huggingface.co)
3. Git installed locally
4. Git LFS installed

### Step 1: Set up Git and Git LFS

```bash
# Initialize git repository
git init

# Install Git LFS (if not already installed)
# Windows (with Git for Windows):
git lfs install

# Track large model files
git lfs track \"*.safetensors\"
git lfs track \"*.bin\"
git lfs track \"LLm_models/**\"

# Add all files
git add .gitattributes
git add .
git commit -m \"Initial commit with Docker deployment\"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: 
aju-gpt (or your preferred name)
3. Description: \"AI Chatbot with RAG using TinyLlama\"
4. Set to **Public** (required for free Hugging Face Spaces)
5. **Don't** initialize with README (you already have one)
6. Click \"Create repository\"

```bash
# Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/raju-gpt.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Hugging Face Spaces

1. **Go to**: https://huggingface.co/spaces
2. **Click**: \"Create new Space\"
3. **Configure**:
   - **Space name**: 
aju-gpt
   - **License**: MIT
   - **SDK**: Select **Docker**
   - **Hardware**: **CPU basic** (free, 16GB RAM)
   - **Visibility**: Public (required for free tier)

4. **Link GitHub Repository**:
   - After creation, go to Space Settings
   - Click \"Repository\" tab
   - Link your GitHub repository
   - Enable auto-sync

5. **Add Environment Secrets**:
   - Go to Space Settings → Variables and secrets
   - Add these secrets:
     `
   SECRET_KEY=your-django-secret-key
   SERPAPI_KEY=your-serpapi-key
   HUGGINGFACE_TOKEN=your-hf-token
   DEBUG=False
   ALLOWED_HOSTS=huggingface.co,hf.space
     `

6. **Rename README**: 
   - In your repo, rename README.md to README_PROJECT.md
   - Rename README_SPACES.md to README.md
   - Commit and push

7. **Wait for Build** (15-20 minutes first time):
   - Hugging Face will automatically build your Docker container
   - Monitor build logs in the Space's \"Build\" tab
   - Once complete, your app will be live!

### Your App URL
```
https://huggingface.co/spaces/YOUR_USERNAME/raju-gpt
```

---

## 🐳 Docker Local Testing

Test your Docker setup locally before deploying:

```bash
# Build the image
docker build -t raju-gpt .

# Run with environment variables
docker run -p 7860:7860 \
  -e SECRET_KEY=your-secret-key \
  -e SERPAPI_KEY=your-api-key \
  -e DEBUG=True \
  raju-gpt

# Or use docker-compose
docker-compose up --build
```

Visit: http://localhost:8000 (docker-compose) or http://localhost:7860 (docker run)

---

## 🚂 Alternative: Railway Deployment

**Cost**: $5/month credit (good for testing)
**RAM**: 8GB available
**Best for**: Small-scale production

### Steps:

1. **Sign up**: https://railway.app (use GitHub login)
2. **New Project** → **Deploy from GitHub repo**
3. **Select** your 
aju-gpt repository
4. **Add Environment Variables**:
   `
   SECRET_KEY=your-secret-key
   SERPAPI_KEY=your-api-key
   DEBUG=False
   ALLOWED_HOSTS=.railway.app
   PORT=8000
   `
5. **Deploy** - Railway auto-detects Dockerfile
6. **Get URL** from Railway dashboard

---

## 🎨 Alternative: Render Deployment

**Cost**: $25/month minimum (Standard plan for 2GB RAM)
**Best for**: If you need more control than HF Spaces

### Steps:

1. **Sign up**: https://render.com
2. **New** → **Web Service**
3. **Connect** GitHub repository
4. **Configure**:
   - **Name**: raju-gpt
   - **Runtime**: Docker
   - **Instance Type**: Standard ($25/month)
   - **Auto-Deploy**: Yes
5. **Environment Variables**: Same as Railway
6. **Create Web Service**

---

## 📊 Platform Comparison

| Platform | Cost | RAM | Pros | Cons |
|----------|------|-----|------|------|
| **HF Spaces** | Free | 16GB | Free, built for ML | CPU only (slow) |
| **Railway** | $5-20/mo | 8GB | Easy, good DX | Credits deplete |
| **Render** | $25/mo | 2GB+ | Reliable, auto-SSL | Expensive for adequate RAM |

---

## 🔧 Environment Variables Reference

Required variables for all platforms:

```env
# Django
SECRET_KEY=<generate-unique-key>
DEBUG=False
ALLOWED_HOSTS=<your-domain>

# API Keys
SERPAPI_KEY=<your-serpapi-key>
HUGGINGFACE_TOKEN=<your-hf-token>

# Database (optional - uses SQLite by default)
DATABASE_URL=<postgres-url>
```

Generate SECRET_KEY:
```bash
python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\"
```

---

## 🐛 Troubleshooting

### Build Fails
- Check Docker logs
- Verify all files are committed
- Ensure Git LFS tracked model files

### App Won't Start
- Check environment variables are set
- Verify SECRET_KEY is defined
- Check logs for migration errors

### Slow Response
- Normal on free CPU tier (10-30 seconds)
- Consider GPU upgrade on HF Spaces ($60/month)
- Or optimize model with quantization

### Model Not Loading
- Verify model files in LLm_models/
- Check Git LFS status: git lfs ls-files
- Re-track if needed: git lfs migrate import --include=\"LLm_models/**\"

---

## 📝 Next Steps

1. ✅ Deploy to Hugging Face Spaces (free)
2. Test the deployment
3. Share your app URL
4. Monitor usage and performance
5. Upgrade to GPU if needed

---

## 🎯 Production Checklist

- [ ] New SECRET_KEY generated
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS configured
- [ ] Environment variables secured
- [ ] Git LFS tracking models
- [ ] .env file NOT committed
- [ ] Health checks working
- [ ] Static files collected
- [ ] Database migrations applied

---

**Questions?** Check the main README.md or open an issue on GitHub.
