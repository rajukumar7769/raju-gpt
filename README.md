# RAJU-GPT - AI Chatbot with RAG

A Django-based AI chatbot application using local LLM models (TinyLlama) with Retrieval Augmented Generation (RAG) via SerpAPI for real-time web search capabilities.

## Features

- 🤖 **Local LLM Integration**: Uses TinyLlama-1.1B-Chat-v1.0 with 4-bit quantization
- 🔍 **RAG (Retrieval Augmented Generation)**: Real-time web search using SerpAPI
- 👤 **User Authentication**: Complete registration, login, and profile management
- 💬 **Chat History**: Persistent chat storage per user
- 📄 **Export Functionality**: Download chat history as PDF or text
- 🎤 **Voice Input**: Web Speech API integration
- 🌓 **Dark/Light Mode**: Toggle between themes
- 📱 **Responsive Design**: Modern glassmorphism UI

## Prerequisites

- Python 3.9+
- CUDA-capable GPU (optional, but recommended for better performance)
- SerpAPI account and API key
- Hugging Face account (for model downloads)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/rajukumar7769/raju-gpt.git
cd raju-gpt
```

### 2. Create and activate virtual environment

```bash
# Create virtual environment
python -m venv myenv

# Activate (Windows)
myenv\Scripts\activate

# Activate (Linux/Mac)
source myenv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy `.env.example` to `.env` and update with your actual values:

```bash
copy .env.example .env
```

Edit `.env` file:
```
SECRET_KEY=your-unique-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

SERPAPI_KEY=your-serpapi-api-key
HUGGINGFACE_TOKEN=your-hugging-face-token
```

**Get your API keys:**
- SerpAPI: https://serpapi.com/ (register for free tier)
- Hugging Face: https://huggingface.co/settings/tokens

### 5. Download the LLM model (First time only)

The model is already included in `LLm_models/custom_model/` directory. If you need to re-download:

```bash
python gpt_app/load_llm.py
```

### 6. Run database migrations

```bash
python manage.py migrate
```

### 7. Create a superuser (optional)

```bash
python manage.py createsuperuser
```

## Running the Application

### Start the development server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

### Default Pages

- `/` - Login page
- `/register/` - User registration
- `/index/` - Main chatbot interface
- `/admin/` - Django admin panel

## Project Structure

```
raju_gpt_proj/
├── gpt_app/                    # Main application
│   ├── models.py              # Database models (Chat_data)
│   ├── views.py               # View logic and LLM integration
│   ├── urls.py                # URL routing
│   ├── config.py              # Configuration (API keys)
│   └── load_llm.py           # Model download script
├── raju_gpt_proj/             # Project settings
│   ├── settings.py            # Django settings
│   └── urls.py                # Root URL configuration
├── templates/                  # HTML templates
│   ├── index.html             # Chat interface
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   ├── profile.html           # User profile
│   └── settings.html          # User settings
├── static/                     # Static files (CSS, JS, images)
├── LLm_models/                # Downloaded LLM models
├── django_cache/              # File-based cache storage
├── db.sqlite3                 # SQLite database
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (not in git)
└── .env.example               # Environment variables template
```

## Usage

### 1. Register an Account
- Go to http://127.0.0.1:8000/register/
- Fill in your details and create an account

### 2. Login
- Use your credentials to login

### 3. Start Chatting
- Type your questions in the chat interface
- Use the microphone button for voice input
- Toggle dark/light mode as preferred
- Export your chat history using the download button

### 4. Features Available
- **Profile**: View your account information
- **Settings**: Change your password
- **Upgrade Plan**: (Placeholder for future premium features)

## Model Configuration

The chatbot uses **TinyLlama-1.1B-Chat-v1.0** with:
- **Quantization**: 4-bit (reduces memory usage)
- **Max tokens**: 300
- **Temperature**: 0.7
- **Top-p**: 0.9
- **Repetition penalty**: 1.2

You can modify these parameters in `gpt_app/views.py` in the `get_response()` function.

## Caching

The model and tokenizer are cached using Django's file-based cache to avoid reloading on every request.

**Clear cache:**
```bash
python clear_cache.py
```

## Database Utilities

Query database statistics:
```bash
python db_qurery.py
```

This will show:
- All registered users
- Chat statistics per user
- Recent chat history

## Troubleshooting

### Model not loading
```bash
# Clear cache and restart
python clear_cache.py
python manage.py runserver
```

### CUDA Out of Memory
- Reduce `max_new_tokens` in views.py
- Use CPU instead (slower): Set `device = torch.device("cpu")`

### SerpAPI errors
- Check your API key in `.env`
- Verify you haven't exceeded your free tier limit

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## Security Notes

⚠️ **Important for Production:**
1. Change `SECRET_KEY` in `.env` to a unique random string
2. Set `DEBUG=False` in production
3. Configure proper `ALLOWED_HOSTS`
4. Use PostgreSQL or MySQL instead of SQLite
5. Set up HTTPS
6. Never commit `.env` file to version control

## Contributing

This is a learning project. Feel free to:
- Report issues
- Suggest improvements
- Submit pull requests

## Tech Stack

- **Backend**: Django 4.2.20
- **AI/ML**: PyTorch, Transformers, TinyLlama
- **Database**: SQLite3 (development)
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **APIs**: SerpAPI (web search)
- **PDF Generation**: ReportLab

## License

Educational/Personal Use

## Credits

- Developed by: Raju
- Model: TinyLlama by TinyLlama team
- Built with Django and Hugging Face Transformers

## Future Enhancements

- [ ] Add conversation context memory
- [ ] Multiple model support
- [ ] File upload for document Q&A
- [ ] Chat export in multiple formats
- [ ] Admin dashboard for monitoring
- [ ] API endpoints for external integration
- [ ] Docker containerization

---

**Need Help?** Check the troubleshooting section or open an issue.
