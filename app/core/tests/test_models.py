from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email="test@outlook.com", password="test123"):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test for creating user with an email successful"""
        email = "test@outlook.com"
        password = "test123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_is_normalised(self):
        """Test that the user's email is normalised"""
        email = "test@OUTLOOK.COM"
        user = get_user_model().objects.create_user(
            email,
            "password"
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test error is raised when creating new user with no email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "test123")

    def test_create_superuser(self):
        """Test creating new superuser"""
        user = get_user_model().objects.create_superuser(
            "admin@outlook.com",
            "admin123"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string represtation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name="test"
        )

        self.assertEqual(str(tag), tag.name)
