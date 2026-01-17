#!/usr/bin/env python
"""
Test the Django endpoint with a POST request
"""
import os
import django
import json

os.environ['DJANGO_SETTINGS_MODULE'] = 'raju_gpt_proj.settings'
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.middleware.csrf import get_token

print("\n" + "="*70)
print("TESTING DJANGO ENDPOINT")
print("="*70 + "\n")

# Create test user
user, created = User.objects.get_or_create(username='testuser')
if created:
    user.set_password('testpass123')
    user.save()
    print(f"✅ Created test user: {user.username}")
else:
    print(f"✅ Using existing user: {user.username}")

# Create Django test client
client = Client()

# Login
print("\n🔐 Logging in...")
login_success = client.login(username='testuser', password='testpass123')
print(f"✅ Login: {login_success}")

# Get CSRF token
print("\n🔑 Getting CSRF token...")
response = client.get('/index/')
csrf_token = response.cookies.get('csrftoken').value if 'csrftoken' in response.cookies else None
print(f"✅ CSRF token: {csrf_token[:20]}..." if csrf_token else "❌ No CSRF token")

# Test message
test_message = "hello"
print(f"\n📨 Sending test message: '{test_message}'")

# Make POST request to get_response
response = client.post(
    '/get-response/',
    data=json.dumps({'message': test_message}),
    content_type='application/json',
    HTTP_X_CSRFTOKEN=csrf_token
)

print(f"Response status: {response.status_code}")
print(f"Response content type: {response.get('Content-Type')}")

if response.status_code == 200:
    try:
        data = response.json()
        print(f"\n✅ Got response!")
        print(f"Response preview: {data.get('response', 'No response')[:150]}...")
    except Exception as e:
        print(f"❌ Error parsing JSON: {e}")
        print(f"Response: {response.content}")
else:
    print(f"\n❌ Error: Status {response.status_code}")
    print(f"Response: {response.content.decode()}")

print("\n" + "="*70)
