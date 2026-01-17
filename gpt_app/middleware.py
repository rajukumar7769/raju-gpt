"""
Custom middleware for RAJU-GPT
"""
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.core.cache import cache
from datetime import datetime, timedelta


class DailyUsageLimitMiddleware(MiddlewareMixin):
    """
    Enforce daily usage limits per user (100 chats per day).
    Resets at midnight.
    """
    MAX_DAILY_CHATS = 100

    def process_request(self, request):
        # Only apply to chat endpoint
        if request.path != '/get-response/' or request.method != 'POST':
            return None

        if not request.user.is_authenticated:
            return None

        # Get today's usage count
        today = datetime.now().date()
        cache_key = f"daily_usage:{request.user.id}:{today}"
        usage = cache.get(cache_key, 0)

        if usage >= self.MAX_DAILY_CHATS:
            return JsonResponse({
                'error': f'Daily limit reached ({self.MAX_DAILY_CHATS} messages per day). Resets at midnight.',
                'status': 'limit_exceeded',
                'limit': self.MAX_DAILY_CHATS,
                'used': usage
            }, status=429)

        # Increment usage
        cache.set(cache_key, usage + 1, timeout=86400)  # 24 hours
        return None
