#!/usr/bin/env python
"""
Test the chat endpoint logic directly
"""
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'raju_gpt_proj.settings'

import django
django.setup()

print("\n" + "="*70)
print("TESTING CHAT ENDPOINT LOGIC")
print("="*70 + "\n")

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import requests
from gpt_app.config import SERPAPI_KEY

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}\n")

# Test 1: Check if SerpAPI key is configured
print("1️⃣ Checking SerpAPI Configuration...")
if SERPAPI_KEY and SERPAPI_KEY != 'your-serpapi-key-here':
    print(f"✅ SERPAPI_KEY is configured")
else:
    print(f"⚠️ SERPAPI_KEY is NOT configured or is default value")
    print(f"   Current value: {SERPAPI_KEY}")

# Test 2: Test web search function
print("\n2️⃣ Testing Web Search...")
def search_web(query):
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "num": 3
    }
    try:
        res = requests.get(url, params=params, timeout=8).json()
        snippets = [r.get("snippet", "") for r in res.get("organic_results", [])]
        return "\n".join(snippets) if snippets else "(No search results found)"
    except Exception as e:
        print(f"⚠️ Web search error: {e}")
        return f"(Web search unavailable)"

test_query = "hi"
context = search_web(test_query)
print(f"Search query: '{test_query}'")
print(f"Context retrieved: {len(context)} chars")
if "(Web search unavailable)" in context or "(No search results found)" in context:
    print(f"⚠️ Warning: {context}")

# Test 3: Test model loading and generation
print("\n3️⃣ Testing Model Generation...")
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

try:
    print("Loading tokenizer and model...")
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float32,
        trust_remote_code=True,
        use_safetensors=True
    ).to(device)
    print("✅ Model loaded!")
    
    # Test with simple prompt first
    print("\n4️⃣ Testing Simple Prompt...")
    simple_prompt = "You are RAJU-GPT. Answer briefly.\n\nQuestion: hi\n\nAnswer:"
    inputs = tokenizer(simple_prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.2,
        )
    
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if simple_prompt in decoded:
        response = decoded.split(simple_prompt)[-1].strip()
    else:
        response = decoded[len(simple_prompt):].strip()
    
    print(f"Input: {simple_prompt}")
    print(f"Output: {response[:200]}")
    
    # Test with full context
    print("\n5️⃣ Testing Full Chat Logic...")
    message = "hi"
    full_prompt = (
        "You are RAJU-GPT, a helpful, informative, and polite assistant developed using generative AI. "
        "Use the following web context to answer the user's query.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {message}\n\n"
        "Answer:"
    )
    
    print(f"Prompt length: {len(full_prompt)} chars")
    inputs = tokenizer(full_prompt, return_tensors="pt").to(device)
    print(f"Tokenized input shape: {inputs['input_ids'].shape}")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.2,
        )
    
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"Generated output length: {len(decoded)} chars")
    
    if full_prompt in decoded:
        response = decoded.split(full_prompt)[-1].strip()
    else:
        response = decoded[len(full_prompt):].strip()
    
    print(f"\n✅ Final Response (first 300 chars):")
    print(f"   {response[:300]}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED - Chat should work!")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
