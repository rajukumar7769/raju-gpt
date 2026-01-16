import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'raju_gpt_proj.settings')

import django
django.setup()

from django.core.management import call_command

# Run migrations
call_command('migrate', '--noinput')
call_command('collectstatic', '--noinput', '--clear')

# Import WSGI application
from raju_gpt_proj.wsgi import application as app
