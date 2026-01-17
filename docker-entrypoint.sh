#!/bin/bash
set -e

echo "=== RAJU-GPT Startup ==="

# Create necessary directories
mkdir -p /app/staticfiles /app/media /app/django_cache

# HF Spaces persistent storage support
if [ -d "/data" ]; then
    echo "✅ Using HF Spaces persistent storage for database..."
    mkdir -p /data
    
    if [ ! -f /data/db.sqlite3 ]; then
        echo "   Creating new persistent database..."
        touch /data/db.sqlite3
    else
        echo "   Using existing persistent database..."
    fi
    
    ln -sf /data/db.sqlite3 /app/db.sqlite3
fi

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "=== Starting RAJU-GPT Application ==="
echo "Server listening on 0.0.0.0:7860"
exec "$@"
