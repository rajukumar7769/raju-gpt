from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
from decouple import config

# --- STEP 1: Login to Hugging Face ---
# Get token from environment variable
HF_TOKEN = config('HUGGINGFACE_TOKEN', default='')
if HF_TOKEN:
    login(HF_TOKEN)
else:
    print("Warning: HUGGINGFACE_TOKEN not found in environment variables")  
# Define model name and path to save locally
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
local_dir = "LLm_models/custom_model"  # You can change this path

# Download and save tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.save_pretrained(local_dir)

model = AutoModelForCausalLM.from_pretrained(model_name)
model.save_pretrained(local_dir)

print(f"Model saved locally to {local_dir}")
