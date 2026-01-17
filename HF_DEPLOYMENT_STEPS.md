# 🤗 HuggingFace Spaces Deployment - Step-by-Step Guide

## ✅ Pre-Deployment Checklist

- [x] Git repository is public
- [x] All code is committed and pushed to GitHub
- [x] Dockerfile is configured
- [x] README_SPACES.md exists
- [x] requirements.txt is up-to-date
- [x] Environment variables are defined

---

## 🚀 Deployment Steps

### Step 1: Verify Your GitHub Repository is Public
```bash
# Check your current remote
git remote -v
# Output should show: origin https://github.com/YOUR_USERNAME/raju-gpt.git

# Make sure your repository is PUBLIC on GitHub
# Visit: https://github.com/YOUR_USERNAME/raju-gpt/settings
```

### Step 2: Go to HuggingFace Spaces
1. Visit: https://huggingface.co/spaces
2. Click: **"Create new Space"**

### Step 3: Configure New Space
Fill in the creation form:
- **Space name**: `raju-gpt` (or your preference)
- **License**: MIT
- **SDK**: **Docker** (important!)
- **Hardware**: **CPU basic** (free tier with 16GB RAM)
- **Visibility**: **Public** (required for free)
- Click: **"Create space"**

### Step 4: Link Your GitHub Repository
After space creation:
1. Go to Space Settings (⚙️ icon)
2. Scroll down to **"Repository"** section
3. Click **"Link a model/dataset/space"**
4. Select your GitHub repo: `raju-gpt`
5. Enable **"Auto-sync"** (optional but recommended)

### Step 5: Add Environment Secrets
In Space Settings → **"Variables and secrets"**:
Add these environment variables:

```
SECRET_KEY=your-django-secret-key-here
DEBUG=False
ALLOWED_HOSTS=huggingface.co,.hf.space
SERPAPI_KEY=your-serpapi-key-if-needed
HUGGINGFACE_TOKEN=your-hf-token-if-needed
DATABASE_URL=your-neon-postgres-url
```

⚠️ **Important**: These are stored securely as secrets

### Step 6: Prepare Your Repository

#### 6a. Set up Git LFS for Large Files
```bash
# Install Git LFS
git lfs install

# Track large model files
git lfs track "*.safetensors"
git lfs track "*.bin"
git add .gitattributes
git commit -m "chore: add git lfs tracking"
git push origin main
```

#### 6b. Rename README Files
```bash
# In your local repo:
# 1. Rename README.md to README_PROJECT.md
# 2. Rename README_SPACES.md to README.md
# 3. Commit and push

git add README.md README_PROJECT.md README_SPACES.md
git commit -m "chore: rename readme for hf spaces"
git push origin main
```

### Step 7: Monitor Deployment

Once you've linked the GitHub repo:
1. HuggingFace will automatically detect the Dockerfile
2. It will start building (first build takes 15-20 minutes)
3. Monitor progress in the **"Build"** tab of your Space
4. Once complete, your app will be live!

### Step 8: Access Your Deployed App

Your app will be available at:
```
https://huggingface.co/spaces/YOUR_USERNAME/raju-gpt
```

---

## 🔧 Troubleshooting

### Build Fails?
- Check the **Build** tab logs for errors
- Ensure all dependencies in `requirements.txt` are pinned to specific versions
- Verify Dockerfile uses correct base image and paths

### App Won't Start?
- Check **"App"** tab logs for runtime errors
- Verify all environment variables are set in Settings
- Check that `docker-entrypoint.sh` has correct permissions

### Database Connection Error?
- Verify `DATABASE_URL` environment variable is set correctly
- Ensure Neon PostgreSQL allows connections from HF Spaces IP ranges
- Check network firewall rules

### Model Loading Slow?
- First request may take 2-3 minutes as model loads
- Subsequent requests are instant
- HuggingFace caches the model in the container

---

## 📊 HuggingFace Spaces Benefits

✅ **Free Tier**:
- 16GB RAM (enough for TinyLlama 1.1B)
- CPU-based (sufficient for inference)
- Automatic HTTPS
- No credit card needed
- Public sharing

✅ **Auto-Scaling**:
- Scales down when inactive (saves resources)
- Scales up on demand (instant on first request)

✅ **GitHub Integration**:
- Auto-sync from your repo
- Push updates = automatic redeploy
- Version control built-in

---

## 🎉 After Deployment

Once live:
1. Share your Space URL: `https://huggingface.co/spaces/YOUR_USERNAME/raju-gpt`
2. Monitor usage in the **"Logs"** tab
3. Update code in your GitHub repo (auto-deploys if auto-sync enabled)
4. Collect user feedback
5. Plan Phase 2 features

---

## 📝 Quick Reference

| Step | Action | Time |
|------|--------|------|
| 1 | Verify GitHub is public | 2 min |
| 2-3 | Create HF Space | 1 min |
| 4 | Link GitHub repo | 2 min |
| 5 | Add environment variables | 3 min |
| 6 | Prepare repository (Git LFS, README) | 5 min |
| 7 | Wait for build | 15-20 min |
| **Total** | | **~30 minutes** |

---

## 🚀 Next Steps (After Deployment Confirmed)

Once your app is live:
- [ ] Test all features in production
- [ ] Monitor logs for errors
- [ ] Collect performance metrics
- [ ] Plan Phase 2 development (streaming, voice, etc.)
- [ ] Implement user feedback

---

**Good luck with deployment! 🚀**
