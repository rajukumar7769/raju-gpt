from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_user, name='login'),  # root URL now shows login page
    path('index/', views.index, name='index'),  # index page moved to /index/
    path("get-response/", views.get_response, name="get_response"),
    path("stream-response/", views.stream_response, name="stream_response"),  # Phase 2.1: Streaming
    path("chat-history/", views.get_chat_history, name="get_chat_history"),
    path("export-chat-as-pdf/", views.export_chat_as_pdf, name="export_chat_as_pdf"),
    path("export-chat-as-json/", views.export_chat_as_json, name="export_chat_as_json"),
    path("clear-chat/", views.clear_chat, name="clear_chat"),
    path("clear-session/", views.clear_session, name="clear_session"),
    path("get-sessions/", views.get_sessions, name="get_sessions"),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('reset-password/<str:uid>/<str:token>/', views.reset_password_confirm, name='reset_password_confirm'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('upgrade-plan/', views.upgrade_plan, name='upgrade_plan'),
    path('settings/update/', views.update_profile, name='update_profile'),
    path('healthz/', views.healthz, name='healthz'),
    # Avatar endpoints
    path('avatar/<str:username>/', views.user_avatar, name='user_avatar'),
    path('avatar/bot/logo/', views.bot_avatar, name='bot_avatar'),
    
    # Conversation Management Endpoints
    path('conversations/create/', views.create_conversation, name='create_conversation'),
    path('conversations/', views.get_conversations, name='get_conversations'),
    path('conversations/<int:conv_id>/delete/', views.delete_conversation, name='delete_conversation'),
    path('conversations/<int:conv_id>/rename/', views.rename_conversation, name='rename_conversation'),
    path('conversations/<int:conv_id>/pin/', views.toggle_pin_conversation, name='toggle_pin_conversation'),
    path('conversations/<int:conv_id>/messages/', views.get_conversation_messages, name='get_conversation_messages'),
    
    # Message Management Endpoints
    path('messages/<int:msg_id>/delete/', views.delete_message, name='delete_message'),
    path('messages/<int:msg_id>/edit/', views.edit_message, name='edit_message'),
    path('messages/<int:msg_id>/regenerate/', views.regenerate_response, name='regenerate_response'),
    
    # Search Endpoint
    path('search/', views.search_conversations, name='search_conversations'),
]
