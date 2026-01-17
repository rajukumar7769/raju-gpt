from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import auth
from django.contrib.auth.models import User
from reportlab.pdfgen import canvas
from gpt_app.models import Chat_data
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM,AutoModelForCausalLM
from django.core.cache import cache
import torch
import json
import warnings
from django.utils import timezone
from .config import SERPAPI_KEY
import requests

warnings.filterwarnings("ignore")
# Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the model/tokenizer and cache them (only once)
# def get_model_and_tokenizer():
#     print("Checking cache for model and tokenizer...")
#     tokenizer = cache.get("flan_t5_tokenizer")
#     model = cache.get("flan_t5_model")
    
#     print("Cached model:", tokenizer is not None, "Cached tokenizer:", model is not None)
#     if tokenizer is None or model is None:
#         print("Loading model for the first time...")
#         tokenizer = AutoTokenizer.from_pretrained("LLm_models/flan-t5-base")
#         model = AutoModelForSeq2SeqLM.from_pretrained("LLm_models/flan-t5-base").to(device)

#         # Set them in Django cache
#         cache.set("flan_t5_tokenizer", tokenizer, None)  # No timeout
#         cache.set("flan_t5_model", model, None)

#     return tokenizer, model
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Global variables for lazy loading
_tokenizer = None
_model = None

def get_model_and_tokenizer():
    global _tokenizer, _model
    
    print("🔍 Checking cache for model and tokenizer...")
    
    # Check global variables first (fastest)
    if _tokenizer is not None and _model is not None:
        print("✅ Using global cached model")
        return _tokenizer, _model
    
    # Check Django cache
    tokenizer = cache.get("custom_tokenizer")
    model = cache.get("custom_model")
    
    if tokenizer is not None and model is not None:
        print("✅ Using Django cached model")
        _tokenizer = tokenizer
        _model = model
        return tokenizer, model
    
    # Check global variables
    if _tokenizer is not None and _model is not None:
        print("✅ Using global model")
        return _tokenizer, _model
    
    print("📥 Loading model for the first time (this may take 5-10 minutes)...")
    print(f"📦 Model: {model_id}")
    print("⏳ Step 1/2: Loading tokenizer...")
    
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    print("✅ Tokenizer loaded!")
    
    print("⏳ Step 2/2: Downloading and loading model (~2.2GB)...")
    print("💡 This is downloading from HuggingFace Hub - please wait...")
    
    model = AutoModelForCausalLM.from_pretrained(
                                                model_id,
                                                torch_dtype=torch.float32,
                                                trust_remote_code=True,
                                                use_safetensors=True
                                            ).to(device)
    
    print("✅ Model loaded successfully!")
    print("💾 Caching for future use...")
    
    # Cache in Django
    cache.set("custom_tokenizer", tokenizer, None)
    cache.set("custom_model", model, None)
    
    # Store globally
    _tokenizer = tokenizer
    _model = model
    
    print("🎉 Model ready!")
    return tokenizer, model

# Don't load at startup - lazy load on first request
# tokenizer, model = get_model_and_tokenizer()

# Home route
@login_required(login_url='login')
def index(request):
    chat_history = Chat_data.objects.filter(user=request.user).order_by('timestamp')
    return render(request, 'index.html',{'chat_history': chat_history})

# @login_required
# def chatbot_view(request):
#     user = request.user
#     chat_history = Chat_data.objects.filter(user=user).order_by('timestamp')
#     return render(request, 'index.html', {'chat_history': chat_history})

# Function to fetch real-time context
def search_web(query):
    """
    Fetch real-time search results from SerpAPI.
    Returns formatted snippets from top 3 results or error message.
    """
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

@csrf_exempt
@login_required
def get_response(request):
    """
    Chat endpoint - receives user message and returns AI response
    """
    if request.method == 'POST':
        try:
            # Parse request
            data = json.loads(request.body)
            message = data.get("message", "").strip()
            
            if not message:
                return JsonResponse({'error': 'Message cannot be empty'}, status=400)
            
            print(f"\n{'='*70}")
            print(f"📨 NEW CHAT REQUEST")
            print(f"{'='*70}")
            print(f"Message: {message}")
            print(f"User: {request.user.username}")
            
            # Step 1: Get web context
            print(f"\n🔍 Step 1: Fetching web context...")
            context = search_web(message)
            print(f"✅ Context retrieved: {len(context)} chars")
            
            # Step 2: Build prompt
            print(f"\n📝 Step 2: Building prompt...")
            prompt = (
                "You are RAJU-GPT, a helpful, informative, and polite assistant developed using generative AI. "
                "Use the following web context to answer the user's query.\n\n"
                f"Context:\n{context}\n\n"
                f"Question: {message}\n\n"
                "Answer:"
            )
            print(f"✅ Prompt built: {len(prompt)} chars")
            
            # Step 3: Load model
            print(f"\n🤖 Step 3: Loading model and tokenizer...")
            tokenizer, model = get_model_and_tokenizer()
            print(f"✅ Model ready")
            
            # Step 4: Tokenize
            print(f"\n🔤 Step 4: Tokenizing input...")
            inputs = tokenizer(prompt, return_tensors="pt").to(device)
            input_length = inputs['input_ids'].shape[1]
            print(f"✅ Tokenized: {input_length} tokens")
            
            # Step 5: Generate response
            print(f"\n⚙️ Step 5: Generating response (max 300 tokens)...")
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
            print(f"✅ Generation complete")
            
            # Step 6: Decode
            print(f"\n📖 Step 6: Decoding output...")
            decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"✅ Decoded: {len(decoded)} chars")
            
            # Step 7: Extract response
            print(f"\n✂️ Step 7: Extracting response...")
            if prompt in decoded:
                response = decoded.split(prompt)[-1].strip()
            else:
                response = decoded[len(prompt):].strip() if len(decoded) > len(prompt) else decoded.strip()
            
            # Clean up response
            response = response[:1000] if len(response) > 1000 else response  # Limit to 1000 chars
            print(f"✅ Final response: {response[:100]}...")
            
            # Step 8: Save to database
            print(f"\n💾 Step 8: Saving to database...")
            Chat_data.objects.create(
                user=request.user,
                user_message=message,
                bot_response=response
            )
            print(f"✅ Saved to database")
            
            print(f"\n{'='*70}")
            print(f"✅ CHAT REQUEST COMPLETED SUCCESSFULLY")
            print(f"{'='*70}\n")
            
            return JsonResponse({
                'response': response,
                'status': 'success'
            })

        except json.JSONDecodeError as e:
            print(f"❌ JSON Decode Error: {str(e)}")
            return JsonResponse({
                'error': 'Invalid JSON format',
                'status': 'error'
            }, status=400)
        
        except Exception as e:
            print(f"\n❌ ERROR IN GET_RESPONSE")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
            # Try to save error to database
            try:
                Chat_data.objects.create(
                    user=request.user,
                    user_message=message if 'message' in locals() else 'ERROR',
                    bot_response=f'Error: {str(e)}'
                )
            except:
                pass
            
            return JsonResponse({
                'error': f'Server error: {str(e)}',
                'status': 'error'
            }, status=500)
    
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)




# Get latest 10 messages from DB
@login_required
def get_chat_history(request):
    history = Chat_data.objects.filter(user=request.user).order_by('-timestamp')[:10]
    lines = [f"User: {chat.message}\nRAJU-GPT: {chat.response}" for chat in reversed(history)]
    return JsonResponse({'history': "\n\n".join(lines)})


# PDF Export of chat history
@login_required
def export_chat_as_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="chat_history.pdf"'

    p = canvas.Canvas(response)
    chat_history = Chat_data.objects.filter(user=request.user).order_by('-timestamp')[:20]
    y_position = 800

    for chat in reversed(chat_history):
        p.drawString(100, y_position, f"User: {chat.message}")
        y_position -= 20
        p.drawString(100, y_position, f"RAJU-GPT: {chat.response}")
        y_position -= 40
        if y_position < 100:
            p.showPage()
            y_position = 800

    p.showPage()
    p.save()
    return response


# Register
def register_user(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('register')

        # Create the new user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.save()

        messages.success(request, "Registration successful. Please login.")
        return redirect('login')

    return render(request, 'register.html',{'now': timezone.now(),})

# Login
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Optional: Add a welcome message after successful login
            # messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    # If user already logged in, redirect to index (optional)
    if request.user.is_authenticated:
        return redirect('index')

    return render(request, 'login.html',{'now': timezone.now(),})

# Logout
def logout_user(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    user = request.user
    return render(request, 'profile.html', {'user': user,'now': timezone.now(),})

@login_required
def settings(request):
    user = request.user
    return render(request, 'settings.html', {'user': user,'now': timezone.now(),})

@login_required
def upgrade_plan(request):
    user = request.user
    # You can add any logic related to plans here
    return render(request, 'upgrade_plan.html', {'user': user,'now': timezone.now(),})



@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user

        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if old_password or new_password or confirm_password:
            if not user.check_password(old_password):
                messages.error(request, "Old password is incorrect.")
            elif new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
            elif len(new_password) < 6:
                messages.error(request, "New password must be at least 6 characters.")
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # keep user logged in
                messages.success(request, "Password updated successfully.")
        else:
            messages.info(request, "No password fields filled.")

        # No profile info update
        return redirect('settings')

    return render(request, 'settings.html', {'user': request.user,'now': timezone.now(),})