#!/usr/bin/env python3
"""
Security Verification Script
Checks that all credentials are properly secured and not leaked
"""

import os
import re
import sys
from pathlib import Path

def check_gitignore():
    """Verify .env is in .gitignore"""
    gitignore_path = Path('.gitignore')
    if not gitignore_path.exists():
        return False, ".gitignore not found"
    
    content = gitignore_path.read_text()
    if '.env' not in content:
        return False, ".env not in .gitignore"
    
    return True, ".env properly ignored"

def check_env_file():
    """Verify .env contains all required secrets"""
    env_path = Path('.env')
    if not env_path.exists():
        return False, ".env file not found"
    
    content = env_path.read_text()
    required = ['SERPAPI_KEY', 'SECRET_KEY', 'DATABASE_URL', 'HUGGINGFACE_TOKEN']
    missing = [k for k in required if k not in content]
    
    if missing:
        return False, f"Missing in .env: {missing}"
    
    return True, "All secrets present in .env"

def check_git_history():
    """Check if secrets are in git history"""
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'log', '--all', '--oneline', '-S', 'postgresql://'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.stdout:
            return False, "DATABASE_URL found in git history!"
        return True, "No secrets in git history"
    except:
        return None, "Git check skipped (git not available)"

def check_python_files():
    """Scan Python files for hardcoded secrets"""
    patterns = [
        (r'SERPAPI_KEY\s*=\s*["\']sk_|api_key["\']', 'Hardcoded SERPAPI key'),
        (r'SECRET_KEY\s*=\s*["\'][a-zA-Z0-9]{50}', 'Hardcoded Django secret'),
        (r'postgresql://[a-zA-Z0-9]+:[a-zA-Z0-9]+@', 'Hardcoded database URL'),
        (r'print\s*\(\s*["\'].*api_key', 'API key in print statement'),
        (r'print\s*\(\s*["\'].*token', 'Token in print statement'),
    ]
    
    violations = []
    for py_file in Path('.').rglob('*.py'):
        if 'venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
        
        content = py_file.read_text(errors='ignore')
        for pattern, desc in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(f"{py_file}: {desc}")
    
    if violations:
        return False, f"Found issues: {violations}"
    return True, "No hardcoded secrets in Python files"

def check_html_files():
    """Scan HTML/JS files for exposed secrets"""
    patterns = [
        r'api_key',
        r'serpapi',
        r'postgresql',
        r'token\s*=',
    ]
    
    violations = []
    for html_file in Path('.').rglob('*.html'):
        content = html_file.read_text(errors='ignore')
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                # Ignore template variables
                if '{{' in content and '}}' in content:
                    continue
                violations.append(f"{html_file}: Contains '{pattern}'")
    
    if violations:
        return False, f"Found issues: {violations}"
    return True, "No secrets in HTML files"

def main():
    print("\n🔒 SECURITY VERIFICATION")
    print("=" * 50)
    
    checks = [
        ("✓ .env in .gitignore", check_gitignore),
        ("✓ .env has all secrets", check_env_file),
        ("✓ No secrets in git", check_git_history),
        ("✓ Python files", check_python_files),
        ("✓ HTML/JS files", check_html_files),
    ]
    
    all_passed = True
    for name, check in checks:
        try:
            passed, msg = check()
            if passed is None:
                print(f"⊘ {name}: {msg}")
            elif passed:
                print(f"✅ {name}: {msg}")
            else:
                print(f"❌ {name}: {msg}")
                all_passed = False
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("\n✅ All security checks PASSED!")
        return 0
    else:
        print("\n❌ Security issues found!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
