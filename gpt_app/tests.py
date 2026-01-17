"""
Comprehensive tests for Raju-GPT application
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from gpt_app.models import Chat_data, UserProfile
from gpt_app.avatar_utils import get_user_initials, get_user_color, generate_avatar_svg, generate_bot_logo_svg
from django.utils import timezone
import json


class AvatarUtilsTestCase(TestCase):
    """Test avatar utility functions"""
    
    def test_get_user_initials_with_full_name(self):
        """Test getting initials from full name"""
        initials = get_user_initials("John Doe", "johndoe")
        self.assertEqual(initials, "JD")
    
    def test_get_user_initials_with_username(self):
        """Test getting initials from username when full name is empty"""
        initials = get_user_initials("", "johndoe")
        self.assertEqual(initials, "JO")
    
    def test_get_user_color_consistency(self):
        """Test that same username produces same color"""
        color1 = get_user_color("johndoe")
        color2 = get_user_color("johndoe")
        self.assertEqual(color1, color2)
    
    def test_generate_avatar_svg(self):
        """Test SVG avatar generation"""
        svg = generate_avatar_svg("John Doe", "johndoe")
        self.assertIn('<svg', svg)
        self.assertIn('JD', svg)


class UserAuthenticationTestCase(TestCase):
    """Test user authentication"""
    
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com',
        }
    
    def test_user_login(self):
        """Test user login"""
        User.objects.create_user(**self.user_data)
        response = self.client.post('/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)


class UserProfileTestCase(TestCase):
    """Test user profile functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.profile = UserProfile.objects.create(user=self.user)
    
    def test_profile_creation(self):
        """Test UserProfile creation"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.theme, 'light')
        self.assertEqual(self.profile.total_chats, 0)


class ChatHistoryTestCase(TestCase):
    """Test chat history functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_chat_creation(self):
        """Test creating a chat message"""
        chat = Chat_data.objects.create(
            user=self.user,
            user_message="Hello",
            bot_response="Hi there!",
            session_id="2024-01-17"
        )
        self.assertEqual(chat.user, self.user)
        self.assertEqual(chat.session_id, "2024-01-17")


class HealthCheckTestCase(TestCase):
    """Test health check endpoint"""
    
    def test_health_endpoint(self):
        """Test /healthz/ endpoint"""
        response = self.client.get('/healthz/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'ok')
