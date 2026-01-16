from django.core.cache import cache

# Clear the custom model cache
cache.delete('custom_model')
cache.delete('custom_tokenizer')

print("Cache cleared successfully!")
print("Cleared keys: custom_model, custom_tokenizer")
