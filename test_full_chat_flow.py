#!/usr/bin/env python
"""
Complete Chat Simulation Test
Mimics exactly what happens when a user sends a chat message on HF Spaces
"""
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'raju_gpt_proj.settings'

import django
django.setup()

print("\n" + "="*80)
print("COMPLETE CHAT FLOW SIMULATION TEST")
print("="*80 + "\n")

import json
from django.contrib.auth.models import User
from gpt_app.models import Chat_data
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import requests
from gpt_app.config import SERPAPI_KEY

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Test parameters
TEST_MESSAGE = "hi"
TEST_USERNAME = "testuser"

print(f"Test Parameters:")
print(f"  Message: '{TEST_MESSAGE}'")
print(f"  Device: {device}")
print(f"  Username: {TEST_USERNAME}\n")

try:
    # Step 1: Get or create test user
    print("1️⃣ Creating/Getting test user...")
    user, created = User.objects.get_or_create(
        username=TEST_USERNAME,
        defaults={'email': f'{TEST_USERNAME}@test.com'}
    )
    print(f"   ✅ User: {user.username} ({('Created' if created else 'Existing')})")
    
    # Step 2: Web search
    print("\n2️⃣ Testing web search...")
    url = "https://serpapi.com/search"
    params = {
        "q": TEST_MESSAGE,
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "num": 3
    }
    try:
        res = requests.get(url, params=params, timeout=8).json()
        snippets = [r.get("snippet", "") for r in res.get("organic_results", [])]
        context = "\n".join(snippets) if snippets else "(No search results found)"
        print(f"   ✅ Context retrieved: {len(context)} chars")
    except Exception as e:
        context = f"(Web search error: {e})"
        print(f"   ⚠️ Web search failed: {e}")
        print(f"   ℹ️ Continuing with error context...")
    
    # Step 3: Build prompt
    print("\n3️⃣ Building prompt...")
    prompt = (
        "You are RAJU-GPT, a helpful, informative, and polite assistant developed using generative AI. "
        "Use the following web context to answer the user's query.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {TEST_MESSAGE}\n\n"
        "Answer:"
    )
    print(f"   ✅ Prompt length: {len(prompt)} chars")
    
    # Step 4: Load model
    print("\n4️⃣ Loading model and tokenizer...")
    model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float32,
        trust_remote_code=True,
        use_safetensors=True
    ).to(device)
    print(f"   ✅ Model loaded")
    
    # Step 5: Tokenize
    print("\n5️⃣ Tokenizing input...")
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    print(f"   ✅ Input tokens: {inputs['input_ids'].shape[1]}")
    
    # Step 6: Generate
    print("\n6️⃣ Generating response...")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.2,
            num_return_sequences=1,
            pad_token_id=tokenizer.eos_token_id,
        )
    print(f"   ✅ Generation complete")
    
    # Step 7: Decode
    print("\n7️⃣ Decoding response...")
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"   ✅ Decoded length: {len(decoded)} chars")
    
    # Step 8: Extract response
    print("\n8️⃣ Extracting response...")
    if prompt in decoded:
        response = decoded.split(prompt)[-1].strip()
    else:
        response = decoded[len(prompt):].strip() if len(decoded) > len(prompt) else decoded.strip()
    
    response = response[:1000] if len(response) > 1000 else response
    print(f"   ✅ Response: {response[:100]}...")
    
    # Step 9: Save to database
    print("\n9️⃣ Saving to database...")
    chat = Chat_data.objects.create(
        user=user,
        user_message=TEST_MESSAGE,
        bot_response=response
    )
    print(f"   ✅ Saved: Chat ID {chat.id}")
    
    # Step 10: Simulate JSON response
    print("\n🔟 Simulating JSON response...")
    json_response = {
        'response': response,
        'status': 'success'
    }
    print(f"   ✅ Response: {json.dumps(json_response, indent=2)[:200]}...")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED - CHAT FLOW IS WORKING!")
    print("="*80)
    print("\n📊 Summary:")
    print(f"   Message: {TEST_MESSAGE}")
    print(f"   Response Length: {len(response)} chars")
    print(f"   Total Time: Complete")
    print(f"   Status: SUCCESS ✅")
    print("\n")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    print("\n" + "="*80)
    print("❌ TEST FAILED")
    print("="*80 + "\n")
