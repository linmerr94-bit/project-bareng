from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):
    """
    Test cases untuk custom User model di platform B2B2C VOLTA.
    """
    
    def setUp(self):
        """Prepare test fixtures"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'full_name': 'Test User',
            'phone': '081234567890',
            'role': 'customer'
        }
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, 'customer')
        self.assertEqual(user.full_name, 'Test User')
        self.assertEqual(user.phone, '081234567890')
        self.assertTrue(user.is_active)
    
    def test_create_brand_user(self):
        """Test creating a brand user"""
        self.user_data['role'] = 'brand'
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.role, 'brand')
    
    def test_create_admin_user(self):
        """Test creating an admin user"""
        self.user_data['role'] = 'admin'
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            full_name='Admin User'
        )
        self.assertEqual(user.role, 'admin')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_phone_uniqueness(self):
        """Test that phone numbers must be unique"""
        User.objects.create_user(**self.user_data)
        
        duplicate_data = self.user_data.copy()
        duplicate_data['username'] = 'otheruser'
        duplicate_data['email'] = 'other@example.com'
        
        with self.assertRaises(Exception):
            User.objects.create_user(**duplicate_data)
    
    def test_user_str_representation(self):
        """Test string representation of user"""
        user = User.objects.create_user(**self.user_data)
        expected = f"testuser (Customer)"
        self.assertEqual(str(user), expected)
