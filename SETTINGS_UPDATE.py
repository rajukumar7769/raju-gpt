"""
Updated settings.py with persistent database support for HF Spaces
Replace the DATABASES section with this code
"""

# Database persistence for HF Spaces
# Check if /data directory exists (HF Spaces persistent storage)
if os.path.exists('/data'):
    # Use persistent storage on HF Spaces
    DATABASE_PATH = '/data/db.sqlite3'
    print("✅ Database: Using HF Spaces persistent storage (/data)")
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': DATABASE_PATH,
        }
    }
elif config('DATABASE_URL', default=''):
    # Use external PostgreSQL if configured
    print("✅ Database: Using external PostgreSQL")
    
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback to local development
    print("ℹ️  Database: Using local development database")
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
