from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from django.test import TestCase
from rest_framework import status

from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")


class PublicIngredientsApiTests(TestCase):
    """Test the publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test private ingredients API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@outlook.com",
            "test123"
        )
        self.client.force_authenticate(self.user)

    def test_get_ingredients_list(self):
        """Test getting a list of ingredients"""
        Ingredient.objects.create(user=self.user, name="Choclate")
        Ingredient.objects.create(user=self.user, name="Sugar")

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients for authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            "test123@outlook.com",
            "test123"
        )
        Ingredient.objects.create(user=user2, name="Salt")

        ingredient = Ingredient.objects.create(user=self.user, name="Vinegar")

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test create a new ingredient success"""
        payload = {"name": "Carrot"}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload["name"]
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test create ingredient fails"""
        payload = {"name": ""}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assinged to recipes"""
        ingredient_1 = Ingredient.objects.create(
            user=self.user,
            name="Apple"
        )
        ingredient_2 = Ingredient.objects.create(
            user=self.user,
            name="Chicken"
        )
        recipe = Recipe.objects.create(
            title="Apple crumble",
            time_minutes=5,
            price=10,
            user=self.user
        )
        recipe.ingredients.add(ingredient_1)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        serializer_1 = IngredientSerializer(ingredient_1)
        serializer_2 = IngredientSerializer(ingredient_2)
        self.assertIn(serializer_1.data, res.data)
        self.assertNotIn(serializer_2.data, res.data)
        
    def test_retrieve_ingredients_assigned_unique(self):
        """Test filtering ingredients by assinged returns unique items"""
        ingredient = Ingredient.objects.create(user=self.user, name="Egg")
        Ingredient.objects.create(user=self.user, name="Cheese")
        recipe_1 = Recipe.objects.create(
            title="Eggs on toast",
            time_minutes=20,
            price=12.00,
            user=self.user
        )
        recipe_2 = Recipe.objects.create(
            title="Eggs benedict",
            time_minutes=30,
            price=15.00,
            user=self.user
        )
        recipe_1.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)
