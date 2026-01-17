#!/usr/bin/env python
"""
Local test script to verify the model response works
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'raju_gpt_proj.settings')
sys.path.insert(0, r'F:\BBSBEC\LLM_Project\LLM_project\raju_gpt_proj')

django.setup()

from django.contrib.auth.models import User
from gpt_app.models import Chat_data
import json

# Test 1: Check if we can access the model
print("=" * 60)
print("TEST 1: Loading Model and Tokenizer")
print("=" * 60)

from gpt_app.views import get_model_and_tokenizer
try:
    tokenizer, model = get_model_and_tokenizer()
    print("✅ Model and tokenizer loaded successfully!")
    print(f"Model type: {type(model)}")
    print(f"Tokenizer type: {type(tokenizer)}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Create test user
print("\n" + "=" * 60)
print("TEST 2: Creating Test User")
print("=" * 60)

test_user, created = User.objects.get_or_create(
    username='test_user',
    defaults={
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
)

if created:
    test_user.set_password('testpass123')
    test_user.save()
    print(f"✅ Test user created: {test_user.username}")
else:
    print(f"✅ Test user exists: {test_user.username}")

# Test 3: Generate response
print("\n" + "=" * 60)
print("TEST 3: Testing Model Response")
print("=" * 60)

import torch
from gpt_app.views import search_web, device

message = "Hello, who are you?"
print(f"Message: {message}")

# Get web context
context = search_web(message)
print(f"Web context: {context[:100]}...")

# Create prompt
prompt = (
    "You are RAJU-GPT, a helpful, informative, and polite assistant developed using generative AI. "
    "Use the following web context to answer the user's query.\n\n"
    f"Context:\n{context}\n\n"
    f"Question: {message}\n\n"
    "Answer:"
)

try:
    print("🔄 Generating response...")
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    print(f"✅ Prompt tokenized")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.2,
            early_stopping=True
        )
    print(f"✅ Response generated")
    
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"Decoded length: {len(decoded)}")
    
    if prompt in decoded:
        response = decoded.split(prompt)[-1].strip()
    else:
        response = decoded[len(prompt):].strip()
    
    print(f"✅ Response: {response}")
    
    # Save to database
    chat = Chat_data.objects.create(
        user=test_user,
        user_message=message,
        bot_response=response
    )
    print(f"✅ Chat saved to database (ID: {chat.id})")
    
except Exception as e:
    print(f"❌ Error generating response: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Verify saved chat
print("\n" + "=" * 60)
print("TEST 4: Verifying Saved Chat")
print("=" * 60)

chats = Chat_data.objects.filter(user=test_user)
print(f"✅ Found {chats.count()} chat(s) for user {test_user.username}")

for chat in chats:
    print(f"\n  User: {chat.user_message}")
    print(f"  Bot: {chat.bot_response[:100]}...")
    print(f"  Timestamp: {chat.timestamp}")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
