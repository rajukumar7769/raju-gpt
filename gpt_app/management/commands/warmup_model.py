"""
Management command to warm up the LLM model.
Usage: python manage.py warmup_model
"""
from django.core.management.base import BaseCommand
from gpt_app.load_llm import get_model_and_tokenizer
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Pre-load and warm up the LLM model to reduce first-response latency'

    def handle(self, *args, **options):
        self.stdout.write('Starting model warmup...')
        
        try:
            model, tokenizer = get_model_and_tokenizer()
            
            # Warm up with a test prompt
            test_prompt = "<|system|>\nYou are a helpful AI assistant.</s>\n<|user|>\nHello</s>\n<|assistant|>"
            inputs = tokenizer(test_prompt, return_tensors="pt")
            
            if model.device.type == 'cuda':
                inputs = {k: v.to(model.device) for k, v in inputs.items()}
            
            # Generate test output
            _ = model.generate(
                **inputs,
                max_new_tokens=10,
                temperature=0.7,
                do_sample=True
            )
            
            self.stdout.write(self.style.SUCCESS('✅ Model warmed up successfully!'))
            self.stdout.write(f'Device: {model.device}')
            self.stdout.write(f'Model: {model.config.model_type}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Model warmup failed: {str(e)}'))
            logger.error(f'Model warmup error: {str(e)}', exc_info=True)
