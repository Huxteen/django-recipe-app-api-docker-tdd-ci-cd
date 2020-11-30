from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status



CREATE_USER_URL = reverse('users:create')
TOKEN_URL = reverse('users:token')
UPDATE_USER_URL = reverse('users:update') 


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (Public)"""
    """Public Test Class does not require the url to be authentication."""

    def setUp(self):
        self.client = APIClient()


    def test_create_valid_user_success(self):
        """Test creating user with valid payload is success."""
        payload = {
            'email':'test@husteen.com',
            'password':'test12345',
            'name':'Husteen Tester',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)


    def test_user_exists(self):
        """Test creating user that already exists fails"""

        payload = {'email':'test@husteen.com', 'password':'testpass'}
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_password_too_short(self):
        """Test that the password must be more than 5 characters."""
        payload = {'email':'test@husteen.com', 'password':'pw'}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)




    # Token TestCase
    def test_create_token_for_user(self):
        """Test that a token is created for the user."""
        payload = {'email':'test@husteen.com', 'password':'testpass'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email='test@husteen.com', password='testpass')
        payload = {'email':'test@husteen.com', 'password':'passed1'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""
        payload = {'email':'test@husteen.com', 'password':'testpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""
        payload = {'email':'test@husteen.com', 'password':'testpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email':'one', 'password':''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    # Manage/Update user endpoint
    def test_retrieve_user_unauthorized(self):
        """Test that authorization is required for users"""
        res = self.client.get(UPDATE_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""
    """Private Test Class requires that url to be authentication."""

    def setUp(self):
        self.user = create_user(
            email='test@husteen.com',
            password='testpass',
            name='Tester Name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(UPDATE_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email':self.user.email
        })


    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the update URL"""
        res = self.client.post(UPDATE_USER_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name':'new tester', 'password':'newtestpass'}

        res = self.client.patch(UPDATE_USER_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
