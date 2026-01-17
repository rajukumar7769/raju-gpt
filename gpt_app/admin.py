from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils.html import format_html
from django.utils.timezone import now
from datetime import timedelta
from .models import Chat, Chat_data, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('theme', 'daily_chat_count', 'total_chats', 'last_activity')
    readonly_fields = ('last_activity',)


class CustomUserAdmin(BaseUserAdmin):
    """Enhanced user admin with stats"""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'chat_count', 'last_chat', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    
    def chat_count(self, obj):
        count = Chat_data.objects.filter(user=obj).count()
        return format_html(f'<strong>{count}</strong> chats')
    chat_count.short_description = 'Total Chats'
    
    def last_chat(self, obj):
        last = Chat_data.objects.filter(user=obj).first()
        if last:
            return last.timestamp.strftime('%Y-%m-%d %H:%M')
        return 'Never'
    last_chat.short_description = 'Last Activity'


@admin.register(Chat_data)
class ChatDataAdmin(admin.ModelAdmin):
    """Enhanced chat data admin"""
    list_display = ('user', 'short_message', 'timestamp', 'session_id')
    list_filter = ('timestamp', 'user')
    search_fields = ('user__username', 'user_message', 'bot_response')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
    
    def short_message(self, obj):
        return obj.user_message[:50] + '...' if len(obj.user_message) > 50 else obj.user_message
    short_message.short_description = 'Message'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User profile admin"""
    list_display = ('user', 'theme', 'daily_chat_count', 'total_chats', 'last_activity')
    list_filter = ('theme', 'last_activity')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('last_activity', 'created_at')


# Register Chat model
admin.site.register(Chat)

# Unregister default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Custom admin site branding
admin.site.site_header = 'Raju GPT Admin'
admin.site.site_title = 'Raju GPT Administration'
admin.site.index_title = 'Dashboard'