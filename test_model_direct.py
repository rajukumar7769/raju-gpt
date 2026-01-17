#!/usr/bin/env python
"""
Direct model test - bypass Django ORM
"""
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'raju_gpt_proj.settings'

import django
django.setup()

print("\n" + "="*70)
print("TESTING MODEL LOADING AND RESPONSE GENERATION")
print("="*70 + "\n")

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

try:
    print(f"\n📥 Loading tokenizer from {model_id}...")
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    print("✅ Tokenizer loaded!")
    
    print(f"\n📥 Loading model...")
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float32,
        trust_remote_code=True,
        use_safetensors=True
    ).to(device)
    print("✅ Model loaded!")
    
    # Test generation
    test_prompt = "Hello, how are you? "
    print(f"\n🔄 Testing generation with prompt: '{test_prompt}'")
    
    inputs = tokenizer(test_prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=50,
            temperature=0.7,
            top_p=0.9,
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"\n✅ Generated response:")
    print(f"   {response}\n")
    
    print("="*70)
    print("✅ MODEL TEST PASSED - Everything works!")
    print("="*70)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
