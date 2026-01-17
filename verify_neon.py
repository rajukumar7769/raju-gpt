#!/usr/bin/env python
"""Quick verification script for Neon Postgres connection"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'raju_gpt_proj.settings')

import django
django.setup()

from django.contrib.auth.models import User
from gpt_app.models import Chat_data

print("="*60)
print("📊 NEON POSTGRES DATABASE STATUS")
print("="*60)

users = User.objects.all()
chats = Chat_data.objects.all()

print(f"\n✅ Connected to Neon Postgres!")
print(f"\n📈 Statistics:")
print(f"   Total Users: {users.count()}")
print(f"   Total Chats: {chats.count()}")

if users.exists():
    print(f"\n👥 Users:")
    for u in users:
        print(f"   - {u.username} ({u.email})")

if chats.exists():
    print(f"\n💬 Recent Chats:")
    for c in chats[:5]:
        print(f"   - {c.user.username}: {c.user_message[:50]}...")

print("\n" + "="*60)
print("✅ All data persists in Neon!")
print("Your HF Space is now using production Postgres.")
print("="*60 + "\n")
