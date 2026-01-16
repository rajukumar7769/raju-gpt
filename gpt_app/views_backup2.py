from django.shortcuts import render
# from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from django.views.decorators.csrf import csrf_exempt
import torch
import json
from django.http import JsonResponse
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from gpt_app.models import Chat  
from transformers import AutoTokenizer,AutoModelForCausalLM

# Function to render the home page
def index(request):
    return render(request, 'index.html')

# # Use GPU if available, else CPU
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# dtype = torch.float16 if torch.cuda.is_available() else torch.float32
# print (f"Using device: {device}")
# print (f"Using dtype: {dtype}")




# Load once globally
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained("gpt2-medium")
model = AutoModelForCausalLM.from_pretrained("gpt2-medium").to(device)

# Set pad token
tokenizer.pad_token = tokenizer.eos_token
model.config.pad_token_id = tokenizer.eos_token_id

@csrf_exempt
def get_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get("message", "")

        # Clear prompt format
        prompt = (
                "You are RAJU-GPT, a helpful, informative, and polite assistant developed using generative artificial intelligence. "
                "You provide accurate, clear, and detailed answers to users' questions on various topics.\n\n"
                "User: {user_message}\n"
                "RAJU-GPT:"
            )


        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(device)
        input_len = inputs['input_ids'].shape[-1]
        max_new_tokens = min(1024 - input_len, 250)

        try:
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    repetition_penalty=1.2,
                    pad_token_id=tokenizer.eos_token_id
                )

            # Decode and extract only Assistant's response
            full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
            if "RAJU-GPT:" in full_output:
                response = full_output.split("RAJU-GPT:")[-1].split("User:")[0].strip()
            else:
                response = full_output.strip()

        except Exception as e:
            response = f"Error occurred: {str(e)}"

        # Save chat
        Chat(message=user_message, response=response).save()
        return JsonResponse({'response': response})

    
def get_chat_history():
    # Placeholder implementation for retrieving chat history
    # Replace this with actual logic to fetch chat history from your database or storage
    chat_history = "User: Hello\nBot: Hi there! How can I help you today?\nUser: Can you tell me a joke?\nBot: Why don't scientists trust atoms? Because they make up everything!"
    return chat_history

def export_chat_as_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="chat_history.pdf"'

    p = canvas.Canvas(response)
    chat_history = get_chat_history()  # Retrieve chat history
    y_position = 800  # Start position for text on the PDF

    # Write each line of chat history to the PDF
    for line in chat_history.split('\n'):
        p.drawString(100, y_position, line)
        y_position -= 20  # Move to the next line

    p.showPage()
    p.save()
    return response
