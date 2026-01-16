#!/bin/bash
set -e

echo \"=== RAJU-GPT Startup ===\"

# Create necessary directories
mkdir -p /app/staticfiles /app/media /app/django_cache

# Run migrations
echo \"Running database migrations...\"
python manage.py migrate --noinput

# Collect static files
echo \"Collecting static files...\"
python manage.py collectstatic --noinput --clear

echo \"=== Starting application ===\"
exec \"$@\"
