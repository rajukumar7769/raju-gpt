# 📊 Database Persistence Solution for HF Spaces

## 🚨 Current Issue

**On HF Spaces, the SQLite database is ephemeral** (temporary storage):
- Every container restart deletes the database
- All user registrations are lost
- All chat history is lost
- Each restart starts with empty database ❌

---

## ✅ Solution: 3 Options

### Option 1: Use HF Spaces Persistent Storage (RECOMMENDED) ⭐

**How it works:**
- HF Spaces provides `/data` directory that persists across restarts
- Database is stored in `/data/db.sqlite3`
- Data survives container restarts

**Setup Steps:**

1. **Update `docker-entrypoint.sh`**:
```bash
#!/bin/bash
set -e

echo "=== RAJU-GPT Startup ==="

# Create necessary directories
mkdir -p /app/staticfiles /app/media /app/django_cache

# Use persistent storage on HF Spaces
if [ -d "/data" ]; then
    echo "Using HF Spaces persistent storage..."
    mkdir -p /data
    if [ ! -f /data/db.sqlite3 ]; then
        touch /data/db.sqlite3
    fi
    # Symlink database to persistent storage
    ln -sf /data/db.sqlite3 /app/db.sqlite3
fi

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "=== Starting application ==="
exec "$@"
```

2. **Update `settings.py`** to point to persistent location:
```python
# Check if /data exists (HF Spaces)
if os.path.exists('/data'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/data/db.sqlite3',
        }
    }
else:
    # Fallback for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

3. **Create `.hfspace_config.yaml`** (optional, for documentation):
```yaml
# HF Spaces Configuration
storage:
  persistent:
    - /data  # Persistent across restarts
  
# Docker will automatically use /data for persistent storage
```

**Benefits:**
- ✅ Data persists across restarts
- ✅ Users kept after restart
- ✅ Chat history preserved
- ✅ Free (HF Spaces provides this)
- ✅ No additional setup needed

**Drawbacks:**
- Limited to ~5GB storage
- Single-instance only
- Good for small projects

---

### Option 2: Use PostgreSQL on Render/Railway (BETTER FOR SCALE)

**How it works:**
- Use managed PostgreSQL database (external)
- HF Spaces connects to remote database
- Data stored remotely, not on container

**Setup Steps:**

1. **Create free PostgreSQL on Render.com** or **Railway.app**:
   - Sign up at https://render.com or https://railway.app
   - Create new PostgreSQL database
   - Copy connection string: `postgresql://user:pass@host:5432/db`

2. **Update `requirements.txt`**:
```
Django==4.2.20
torch==2.0.0
transformers==4.36.0
huggingface-hub==0.30.2
requests==2.31.0
reportlab==4.0.0
python-decouple==3.8
gunicorn==21.2.0
whitenoise==6.6.0
dj-database-url==2.1.0
psycopg2-binary==2.9.9  # ← For PostgreSQL
numpy<2.0
```

3. **Update `settings.py`**:
```python
import dj_database_url

# Check for DATABASE_URL (HF Spaces env var)
if config('DATABASE_URL', default=''):
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback to SQLite locally
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

4. **Set in HF Spaces Settings**:
   - Go to Space Settings → Variables and secrets
   - Add: `DATABASE_URL=postgresql://user:pass@host:5432/db`

**Benefits:**
- ✅ Unlimited storage
- ✅ Data persists forever
- ✅ Can scale to multiple instances
- ✅ Professional solution
- ✅ Works across HF Spaces restarts

**Drawbacks:**
- Need to set up external database
- Slight latency for queries
- May need to pay after free tier

---

### Option 3: Use HF Spaces Dataset (Advanced)

**How it works:**
- Create companion HF Dataset
- Store database snapshots there
- Restore on startup

**Benefits:**
- ✅ Version control for database
- ✅ Backup functionality

**Drawbacks:**
- ❌ Complex setup
- ❌ Slow for real-time updates
- ❌ Not recommended for chat app

---

## 🎯 Recommendation: Option 1 (Persistent Storage)

**For your use case** (RAJU-GPT chat), I recommend **Option 1**:

**Why:**
- ✅ Easiest setup (just update 2 files)
- ✅ Works on HF Spaces free tier
- ✅ No additional cost
- ✅ Perfect for your scale
- ✅ Users won't lose data

---

## 📋 Implementation Plan

### File 1: Update `docker-entrypoint.sh`

```bash
#!/bin/bash
set -e

echo "=== RAJU-GPT Startup ==="

# Create necessary directories
mkdir -p /app/staticfiles /app/media /app/django_cache

# HF Spaces persistent storage
if [ -d "/data" ]; then
    echo "✅ Using HF Spaces persistent storage..."
    mkdir -p /data
    if [ ! -f /data/db.sqlite3 ]; then
        echo "Creating new persistent database..."
        touch /data/db.sqlite3
    else
        echo "Using existing persistent database..."
    fi
    # Symlink to persistent location
    ln -sf /data/db.sqlite3 /app/db.sqlite3
fi

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "=== Starting application ==="
exec "$@"
```

### File 2: Update `raju_gpt_proj/settings.py` (Add this after line 88):

```python
# Database persistence for HF Spaces
# Check if /data directory exists (HF Spaces persistent storage)
import os

if os.path.exists('/data'):
    # Use persistent storage on HF Spaces
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/data/db.sqlite3',
        }
    }
    print("✅ Database: Using HF Spaces persistent storage (/data)")
else:
    # Fallback to local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("ℹ️ Database: Using local development database")
```

---

## 🧪 Testing

### Test 1: Local Development
```bash
python manage.py migrate
python manage.py runserver

# Register user: testuser/test123
# Send chat: "hi"
# Data should be in db.sqlite3
```

### Test 2: Docker Locally
```bash
docker build -t raju-gpt .
docker run -p 7860:7860 --env-file .env raju-gpt

# Register user
# Send chat
# Stop container (Ctrl+C)
# Run again: docker run -p 7860:7860 --env-file .env raju-gpt
# ✅ User and chat history should still exist!
```

### Test 3: HF Spaces
1. Deploy updated code
2. Register user
3. Send messages
4. Wait for restart (or restart manually)
5. ✅ User and chat history should persist

---

## 📊 What Gets Stored

With persistent storage, these are saved:

```
✅ User registrations
✅ Chat messages
✅ Chat responses
✅ User profiles
✅ User settings
✅ Database schema

❌ NOT stored (ephemeral):
- Django cache files
- Static files (recreated on start)
- Temp files
```

---

## ⚠️ Important Notes

1. **First Deploy**: Database will be empty (migrations run on startup)
2. **Restart**: Data preserved ✅
3. **Update Code**: Only data deleted if you explicitly reset
4. **Backup**: Make periodic backups of `/data/db.sqlite3`

---

## 🚀 Quick Implementation Steps

1. **Update `docker-entrypoint.sh`** - Add persistent storage logic
2. **Update `settings.py`** - Check for `/data` directory
3. **Test locally** - Verify data persists after restart
4. **Push to GitHub** - Git add, commit, push
5. **HF Spaces auto-deploys** - Data will now persist!

---

## 📈 Expected Results

**Before (without fix):**
```
Restart 1: User registers → Data exists
Restart 2: ❌ User gone
Restart 3: ❌ New empty database
```

**After (with fix):**
```
Restart 1: User registers → Data exists
Restart 2: ✅ User still exists
Restart 3: ✅ User still exists
Restart N: ✅ User still exists forever!
```

---

## ✨ Advanced: Multiple Instances

If you later need multiple HF Spaces instances sharing data:

**Use PostgreSQL** (Option 2):
- Multiple instances → 1 PostgreSQL database
- Perfect for scaling
- Easy horizontal scaling

```
HF Space 1 ──┐
HF Space 2 ──┼──► PostgreSQL (shared)
HF Space 3 ──┘

All instances read/write same database ✅
```

---

**Ready to implement?** Let me know and I'll update your files! 🚀
