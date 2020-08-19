from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test public user API"""

    def setUp(self):
        self.client = APIClient()
        self.payload = {
            "email": "test@outlook.com",
            "password": "test123",
            "name": "test"
        }

    def test_create_valid_user_success(self):
        """Test user is created successfuly"""
        res = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(self.payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_exists(self):
        """Test user create when user already exist"""
        create_user(**self.payload)
        res = self.client.post(CREATE_USER_URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password is longer 5 characters"""
        res = self.client.post(CREATE_USER_URL, {
            "email": "test@outlook.com",
            "password": "short"
        })

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=self.payload["email"]
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is made for user"""
        create_user(**self.payload)
        res = self.client.post(TOKEN_URL, self.payload)

        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_with_invalid_creds(self):
        """Test token is not created when passed invalid creds"""
        create_user(**self.payload)
        res = self.client.post(TOKEN_URL, {
            "email": "test@outlook.com",
            "password": "wrong"
        })

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test token is not created when user doesn't exist"""
        res = self.client.post(TOKEN_URL, self.payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_fields(self):
        """Test token is not created when fields are missing"""
        res = self.client.post(
            TOKEN_URL, {"email": "test@outlook.com", "password": ""})

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test auth is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API endpoints that require auth"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="test@outlook.com",
            password="test123",
            name="test"
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile_success(self):
        """Test get profile of the user that logged in"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            "name": self.user.name,
            "email": self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test that post not allowed on the ME_URL"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile_success(self):
        """Test updating profile of the user"""
        res = self.client.get(ME_URL)
        payload = {
            "name": "update name",
            "password": "updatepassword"
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
