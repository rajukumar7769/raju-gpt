from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Chat(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.id}: {self.message[:20]}..."
    
class Conversation(models.Model):
    """Represents a conversation/chat session"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=255, default='New Conversation')
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_latest_message_preview(self):
        """Get preview of latest message for UI"""
        latest = self.messages.order_by('-timestamp').first()
        if latest:
            text = latest.user_message[:50] + "..." if len(latest.user_message) > 50 else latest.user_message
            return text
        return "Empty conversation"


class Chat_data(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    regeneration_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['session_id']),
            models.Index(fields=['conversation']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"


class UserProfile(models.Model):
    """Extended user profile for preferences and stats"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    theme = models.CharField(max_length=10, default='dark', choices=[('light', 'Light'), ('dark', 'Dark')])
    temperature = models.FloatField(default=0.7, help_text="Model temperature: 0.0-2.0")
    top_p = models.FloatField(default=0.9, help_text="Top-p sampling: 0.0-1.0")
    system_prompt = models.TextField(default="You are a helpful AI assistant.", blank=True)
    daily_chat_count = models.IntegerField(default=0)
    total_chats = models.IntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    model_name = models.CharField(max_length=100, default="TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    
    def __str__(self):
        return f"{self.user.username}'s profile"