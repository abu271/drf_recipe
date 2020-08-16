from django.test import TestCase
from django.contrib.auth import get_user_model


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
