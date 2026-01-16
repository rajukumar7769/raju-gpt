#!/usr/bin/env python3
"""
Auto-upload to Hugging Face Space
"""
import os
import sys
from pathlib import Path
from huggingface_hub import HfApi, HfFolder

# Configuration
REPO_ID = "kumarraju7769/raju-gpt"
REPO_TYPE = "space"
TOKEN = HfFolder.get_token()  # Uses stored HF token

if not TOKEN:
    print("❌ HF token not found. Run: huggingface-cli login")
    sys.exit(1)

# Files/folders to upload
UPLOAD_ITEMS = [
    "Dockerfile",
    "docker-entrypoint.sh", 
    "requirements-prod.txt",
    "manage.py",
    "raju_gpt_proj",
    "gpt_app",
    "templates",
    "static",
]

# Items to exclude from directories
EXCLUDE = {"myenv", "LLm_models", "django_cache", ".git", "__pycache__", ".pytest_cache", "*.pyc"}

def should_exclude(path_str):
    """Check if path should be excluded"""
    path_obj = Path(path_str)
    for exclude_item in EXCLUDE:
        if exclude_item in path_obj.parts or path_obj.name == exclude_item:
            return True
    return False

def upload_files():
    """Upload files to HF Space"""
    api = HfApi()
    
    print(f"🚀 Uploading to {REPO_ID} ({REPO_TYPE})...")
    print(f"Using token: {TOKEN[:10]}...\n")
    
    uploaded = []
    for item in UPLOAD_ITEMS:
        if not Path(item).exists():
            print(f"⚠️  Skipped (not found): {item}")
            continue
        
        if Path(item).is_file():
            # Upload single file
            print(f"📤 Uploading file: {item}")
            api.upload_file(
                path_or_fileobj=item,
                path_in_repo=item,
                repo_id=REPO_ID,
                repo_type=REPO_TYPE,
                token=TOKEN,
            )
            uploaded.append(item)
            print(f"   ✅ Done")
        else:
            # Upload directory
            print(f"📂 Uploading folder: {item}/")
            api.upload_folder(
                folder_path=item,
                repo_id=REPO_ID,
                repo_type=REPO_TYPE,
                token=TOKEN,
                allow_patterns=["**"],
                ignore_patterns=list(EXCLUDE),
                create_pr=False,
            )
            uploaded.append(item)
            print(f"   ✅ Done")
    
    print(f"\n✨ Uploaded {len(uploaded)} items to HF Space!")
    print(f"🔗 View at: https://huggingface.co/spaces/{REPO_ID}")
    print(f"\n⚠️  Next: Add secrets in Space Settings → Variables and secrets")
    print(f"   - SECRET_KEY")
    print(f"   - SERPAPI_KEY") 
    print(f"   - HUGGINGFACE_TOKEN")
    print(f"   - DEBUG=False")

if __name__ == "__main__":
    try:
        upload_files()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
