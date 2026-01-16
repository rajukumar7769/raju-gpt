from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
import requests
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from .models import Chat_data  # Your model for saving chats
from config import SERPAPI_KEY


# Load model once at module level
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto",
    load_in_4bit=True  # Requires bitsandbytes installed
)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Function to fetch real-time context
def search_web(query):
    serpapi_key = "your_serpapi_key_here"  # Replace with your key
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
        return "\n".join(snippets)
    except Exception as e:
        return f"(Web search failed: {e})"

@csrf_exempt
@login_required
def get_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get("message", "")

        # 🔍 Step 1: Get context from web
        context = search_web(message)

        # 🧠 Step 2: Construct prompt using RAG
        prompt = (
            "You are RAJU-GPT, a helpful, informative, and polite assistant developed using generative AI. "
            "Use the following web context to answer the user's query.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {message}\n\n"
            "Answer:"
        )

        try:
            inputs = tokenizer(prompt, return_tensors="pt").to(device)

            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=300,
                    temperature=0.7,
                    top_p=0.9,
                    repetition_penalty=1.2,
                    early_stopping=True
                )

            decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Optional: trim the prompt part out of the full decoded output
            response = decoded[len(prompt):].strip()

        except Exception as e:
            response = f"Error occurred: {str(e)}"

        # 💾 Save chat for the logged-in user
        Chat_data.objects.create(user=request.user, user_message=message, bot_response=response)

        return JsonResponse({'response': response})
