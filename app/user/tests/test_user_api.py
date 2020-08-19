from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test public user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test user is created successfuly"""
        payload = {
            "email": "test@outlook.com",
            "password": "test123",
            "name": "test"
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_exists(self):
        """Test user create when user already exist"""
        payload = {
            "email": "test@outlook.com",
            "password": "test123",
            "name": "test"
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password is longer 5 characters"""
        payload = {
            "email": "test@outlook.com",
            "password": "ha",
            "name": "test"
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is made for user"""
        payload = {
            "email": "test@outlook.com",
            "password": "test123",
            "name": "test"
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn("token", res.data)
        self.assertEqaul(res.status_code, status.HTTP_200_OK)

    def test_create_token_with_invalid_creds(self):
        """Test token is not created when passed invalid creds"""
        create_user(email="test@outlook.com", password="test123")
        payload = {
            "email": "test@outlook.com",
            "password": "wrong"
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test token is not created when user doesn't exist"""
        payload = {
            "email": "test@outlook.com",
            "password": "test123"
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_fields(self):
        """Test token is not created when fields are missing"""
        res = self.client.post(
            TOKEN_URL, {"email": "test@outlook.com", "password": ""})

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
