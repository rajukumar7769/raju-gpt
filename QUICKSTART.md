# 🚀 Quick Start - Deploy to Hugging Face Spaces

## Step 1: Initialize Git & Git LFS

```powershell
# Initialize git
git init

# Install Git LFS (if not already)
git lfs install

# Track large model files
git lfs track "*.safetensors"
git lfs track "*.bin"
git lfs track "LLm_models/**"

# Add and commit
git add .gitattributes
git add .
git commit -m "Initial commit - RAJU-GPT with Docker deployment"
```

## Step 2: Push to GitHub

1. Create new repository on GitHub: https://github.com/new
   - Name: 
aju-gpt
   - Public visibility (required for free HF Spaces)
   - Don't initialize with README

2. Push your code:
```powershell
git remote add origin https://github.com/YOUR_USERNAME/raju-gpt.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy to Hugging Face Spaces

1. Go to: https://huggingface.co/spaces
2. Click "Create new Space"
3. Configure:
   - Name: 
aju-gpt
   - SDK: **Docker**
   - Hardware: **CPU basic (free)** - 16GB RAM
   - Visibility: Public

4. Link GitHub:
   - Settings → Repository
   - Link your GitHub repo
   - Enable auto-sync

5. Add Secrets (Settings → Variables and secrets):
   ```
   SECRET_KEY=your-django-secret-key
   SERPAPI_KEY=your-serpapi-key
   HUGGINGFACE_TOKEN=your-hf-token
   DEBUG=False
   ALLOWED_HOSTS=huggingface.co,hf.space
   ```

6. Rename README files:
   ```powershell
   Rename-Item README.md README_PROJECT.md
   Rename-Item README_SPACES.md README.md
   git add .
   git commit -m "Prepare for HF Spaces"
   git push
   ```

## Your App Will Be Live At:
```
https://huggingface.co/spaces/YOUR_USERNAME/raju-gpt
```

⏱️ First build takes ~15-20 minutes
📊 Monitor build: Space → "Build" tab
✅ Once complete, register and start chatting!

---

## Test Locally First (Optional)

```powershell
# Build Docker image
docker build -t raju-gpt .

# Run container
docker run -p 7860:7860 --env-file .env raju-gpt

# Or use docker-compose
docker-compose up
```

Visit: http://localhost:7860

---

## Need Help?
- Full guide: See DEPLOYMENT.md
- Issues: Check Django logs in HF Space
- Questions: Open GitHub issue

**That's it! Your AI chatbot will be live on Hugging Face Spaces for FREE! 🎉**
