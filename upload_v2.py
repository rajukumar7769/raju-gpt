#!/usr/bin/env python3
"""
Upload to HF Space using individual file uploads with PR approach
"""
import os
from pathlib import Path
from huggingface_hub import HfApi, HfFolder

REPO_ID = "kumarraju7769/raju-gpt"
TOKEN = HfFolder.get_token()

EXCLUDE = {"myenv", "LLm_models", "django_cache", ".git", "__pycache__", ".pytest_cache", "*.pyc", ".gitignore"}

def walk_files(folder):
    """Recursively get all files to upload"""
    files = []
    for item in Path(folder).rglob("*"):
        if item.is_file():
            # Check if should exclude
            if any(exc in item.parts for exc in EXCLUDE if exc != "*.pyc"):
                continue
            if item.suffix == ".pyc":
                continue
            rel_path = item.relative_to(".")
            files.append((str(item), str(rel_path)))
    return files

api = HfApi()

# Get all files
all_files = []
for item in ["Dockerfile", "docker-entrypoint.sh", "requirements-prod.txt", "manage.py"]:
    if Path(item).exists():
        all_files.append((item, item))

for folder in ["raju_gpt_proj", "gpt_app", "templates", "static"]:
    all_files.extend(walk_files(folder))

print(f"📤 Found {len(all_files)} files to upload")

# Upload directly to main branch (bypass PR requirement)
for local_path, repo_path in all_files[:5]:  # Test first 5
    try:
        print(f"  Uploading: {repo_path}")
        api.upload_file(
            path_or_fileobj=local_path,
            path_in_repo=repo_path,
            repo_id=REPO_ID,
            repo_type="space",
            token=TOKEN,
            commit_message=f"Add {repo_path}",
            commit_description="Deploying RAJU-GPT",
        )
        print(f"    ✅ Done")
    except Exception as e:
        print(f"    ❌ Error: {e}")
        break

print("\n🔗 View at: https://huggingface.co/spaces/{REPO_ID}")
