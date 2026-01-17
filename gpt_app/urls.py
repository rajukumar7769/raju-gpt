from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_user, name='login'),  # root URL now shows login page
    path('index/', views.index, name='index'),  # index page moved to /index/
    path("get-response/", views.get_response, name="get_response"),
    path("chat-history/", views.get_chat_history, name="get_chat_history"),
    path("export-chat-as-pdf/", views.export_chat_as_pdf, name="export_chat_as_pdf"),
    path("clear-chat/", views.clear_chat, name="clear_chat"),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('upgrade-plan/', views.upgrade_plan, name='upgrade_plan'),
    path('settings/update/', views.update_profile, name='update_profile'),
    path('healthz/', views.healthz, name='healthz'),

]