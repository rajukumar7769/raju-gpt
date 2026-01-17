from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import auth
from django.contrib.auth.models import User
from django.db.models import Count, Min, Max
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

# Disable torch.compile to avoid issues with older PyTorch versions
import os
os.environ['TORCH_COMPILE_DISABLE'] = '1'

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
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        print("✅ Tokenizer loaded!")
    except Exception as e:
        print(f"❌ Tokenizer loading failed: {str(e)}")
        raise
    
    print("⏳ Step 2/2: Downloading and loading model (~2.2GB)...")
    print("💡 This is downloading from HuggingFace Hub - please wait...")
    
    try:
        # Disable torch.compile to avoid compatibility issues
        os.environ['TORCH_COMPILE_DISABLE'] = '1'
        
        model = AutoModelForCausalLM.from_pretrained(
                                                    model_id,
                                                    torch_dtype=torch.float32,
                                                    trust_remote_code=True,
                                                    use_safetensors=True,
                                                    load_in_4bit=False  # Disable 4bit to avoid compilation issues
                                                ).to(device)
        print("✅ Model loaded successfully!")
    except Exception as e:
        print(f"❌ Model loading failed: {str(e)}")
        # Try without 4bit loading
        try:
            print("⏳ Retrying model loading without advanced features...")
            model = AutoModelForCausalLM.from_pretrained(
                                                        model_id,
                                                        torch_dtype=torch.float32,
                                                        trust_remote_code=True
                                                    ).to(device)
            print("✅ Model loaded with fallback settings!")
        except Exception as e2:
            print(f"❌ Model loading failed on retry: {str(e2)}")
            raise
    
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

@csrf_protect
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

            # Basic validation
            if not message:
                return JsonResponse({'error': 'Message cannot be empty'}, status=400)
            if len(message) > 1000:
                message = message[:1000]

            # Simple per-user rate limiting
            if _rate_limited(request.user.id):
                return JsonResponse({'error': 'Too many requests. Please wait a moment and try again.'}, status=429)
            
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
            
            # Generate session_id (use date for simple grouping)
            session_id = timezone.now().strftime('%Y-%m-%d')
            
            Chat_data.objects.create(
                user=request.user,
                user_message=message,
                bot_response=response,
                session_id=session_id
            )
            
            # Update user profile stats
            try:
                from .models import UserProfile
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                profile.total_chats += 1
                profile.daily_chat_count += 1
                profile.save()
            except Exception as e:
                print(f"⚠️ Profile update failed: {str(e)}")
            
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




def _rate_limited(user_id: int, limit: int = 20, window_seconds: int = 300) -> bool:
    """Simple per-user sliding window rate limiter using Django cache.
    Returns True if over the limit.
    """
    key = f"rl:{user_id}"
    data = cache.get(key) or {"count": 0}
    count = int(data.get("count", 0)) + 1
    data["count"] = count
    # Set/refresh TTL for window
    cache.set(key, data, timeout=window_seconds)
    return count > limit

# Get latest messages from DB as JSON
@login_required
def get_chat_history(request):
    qs = Chat_data.objects.filter(user=request.user).order_by('-timestamp')[:20]
    items = [
        {
            "timestamp": chat.timestamp.isoformat(),
            "user_message": chat.user_message,
            "bot_response": chat.bot_response,
        }
        for chat in reversed(qs)
    ]
    return JsonResponse({'items': items})


# PDF Export of chat history
@login_required
def clear_chat(request):
    if request.method == 'POST':
        Chat_data.objects.filter(user=request.user).delete()
        return JsonResponse({'status': 'cleared'})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def clear_session(request):
    """Clear chat history for a specific session/date"""
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        if session_id:
            Chat_data.objects.filter(user=request.user, session_id=session_id).delete()
            return JsonResponse({'status': 'session_cleared', 'session_id': session_id})
        return JsonResponse({'error': 'session_id required'}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def get_sessions(request):
    """Get all conversation sessions grouped by date"""
    from datetime import date, timedelta
    
    sessions = Chat_data.objects.filter(
        user=request.user
    ).values('session_id').annotate(
        message_count=Count('id'),
        first_message=Min('timestamp'),
        last_message=Max('timestamp')
    ).order_by('-last_message')
    
    result = []
    for session in sessions:
        result.append({
            'session_id': session['session_id'],
            'message_count': session['message_count'],
            'first_message': session['first_message'].isoformat() if session['first_message'] else None,
            'last_message': session['last_message'].isoformat() if session['last_message'] else None,
        })
    
    return JsonResponse({'sessions': result})


@login_required
def export_chat_as_json(request):
    """Export chat history as JSON file"""
    chat_history = Chat_data.objects.filter(user=request.user).order_by('-timestamp')[:100]
    
    data = {
        'user': request.user.username,
        'export_date': timezone.now().isoformat(),
        'total_chats': chat_history.count(),
        'chats': [
            {
                'timestamp': chat.timestamp.isoformat(),
                'user_message': chat.user_message,
                'bot_response': chat.bot_response,
                'session_id': chat.session_id
            }
            for chat in reversed(chat_history)
        ]
    }
    
    response = JsonResponse(data)
    response['Content-Disposition'] = f'attachment; filename="chat_history_{request.user.username}.json"'
    return response


@login_required
def export_chat_as_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="chat_history.pdf"'

    p = canvas.Canvas(response)
    chat_history = Chat_data.objects.filter(user=request.user).order_by('-timestamp')[:20]
    y_position = 800

    for chat in reversed(chat_history):
        p.drawString(100, y_position, f"User: {chat.user_message}")
        y_position -= 20
        p.drawString(100, y_position, f"RAJU-GPT: {chat.bot_response}")
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
        
        # Create user profile
        from .models import UserProfile
        UserProfile.objects.create(user=user)

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


def forgot_password(request):
    """Display forgot password form"""
    return render(request, 'forgot_password.html')


def reset_password(request):
    """Handle password reset request"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email=email)
            # Generate reset token
            from django.contrib.auth.tokens import default_token_generator
            token = default_token_generator.make_token(user)
            
            # Store token in cache for 30 minutes
            cache.set(f'reset_token_{user.id}', token, timeout=1800)
            
            messages.success(request, 'If an account with this email exists, you will receive a password reset link.')
            return redirect('login')
        except User.DoesNotExist:
            messages.success(request, 'If an account with this email exists, you will receive a password reset link.')
            return redirect('login')
    
    return render(request, 'forgot_password.html')


def reset_password_confirm(request, uid, token):
    """Confirm and process password reset"""
    try:
        user_id = int(uid)
        user = User.objects.get(id=user_id)
        
        # Verify token
        from django.contrib.auth.tokens import default_token_generator
        if not default_token_generator.check_token(user, token):
            messages.error(request, 'Invalid or expired reset link.')
            return redirect('login')
        
        if request.method == 'POST':
            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirm_password', '')
            
            if password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'reset_password_confirm.html', {'uid': uid, 'token': token})
            
            if len(password) < 6:
                messages.error(request, 'Password must be at least 6 characters.')
                return render(request, 'reset_password_confirm.html', {'uid': uid, 'token': token})
            
            user.set_password(password)
            user.save()
            
            # Clear cached token
            cache.delete(f'reset_token_{user.id}')
            
            messages.success(request, 'Password reset successful. Please login.')
            return redirect('login')
        
        return render(request, 'reset_password_confirm.html', {'uid': uid, 'token': token})
    
    except (ValueError, User.DoesNotExist):
        messages.error(request, 'Invalid reset link.')
        return redirect('login')


@login_required
def profile(request):
    user = request.user
    
    # Get or create user profile
    from .models import UserProfile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Get chat stats
    total_chats = Chat_data.objects.filter(user=user).count()
    
    # Get today's chat count
    from datetime import date
    today = date.today()
    today_chats = Chat_data.objects.filter(
        user=user,
        timestamp__date=today
    ).count()
    
    context = {
        'user': user,
        'profile': profile,
        'total_chats': total_chats,
        'today_chats': today_chats,
        'now': timezone.now(),
    }
    
    return render(request, 'profile.html', context)

@login_required
def settings(request):
    user = request.user
    
    # Get or create user profile
    from .models import UserProfile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        # Handle theme change
        theme = request.POST.get('theme')
        if theme in ['light', 'dark']:
            profile.theme = theme
            profile.save()
            messages.success(request, f"Theme changed to {theme} mode.")
            return redirect('settings')
    
    context = {
        'user': user,
        'profile': profile,
        'now': timezone.now(),
    }
    
    return render(request, 'settings.html', context)

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


# Health check endpoint
def healthz(request):
    try:
        # Minimal DB ping
        Chat_data.objects.all().count()
        return JsonResponse({"status": "ok"})
    except Exception as e:
        return JsonResponse({"status": "error", "detail": str(e)}, status=500)

# Custom error handlers
def custom_404(request, exception=None):
    """Custom 404 error page"""
    return render(request, '404.html', status=404)


def custom_500(request):
    """Custom 500 error page"""
    return render(request, '500.html', status=500)


# Avatar endpoints
def user_avatar(request, username):
    """Serve user avatar as SVG"""
    from .avatar_utils import generate_avatar_svg
    
    try:
        user = User.objects.get(username=username)
        svg = generate_avatar_svg(user.get_full_name(), user.username)
        return HttpResponse(svg, content_type='image/svg+xml')
    except User.DoesNotExist:
        # Return default avatar
        svg = generate_avatar_svg('', username)
        return HttpResponse(svg, content_type='image/svg+xml')


def bot_avatar(request):
    """Serve bot logo as SVG"""
    from .avatar_utils import generate_bot_logo_svg
    
    svg = generate_bot_logo_svg()
    return HttpResponse(svg, content_type='image/svg+xml')
