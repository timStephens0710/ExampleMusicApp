from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from ..models import OneTimeToken, CustomUser
from ..common.utils import generate_one_time_token


class UsersManagersTests(TestCase):
    '''
    The following test case contains positive and negative test cases for the CustomUserModel 

    The 'get_user_model' will pull the CustomeUser model from models.py, because we hardcode this in the 
    AUTH_USER_MODEL argument in settings.py.
    '''
    def test_create_user_positive(self):
        user = CustomUser.objects.create_user(
            email='test@user.com'
            , password='M3ep!234'
            , username = 'simple_john'
            )
        self.assertEqual(user.email, 'test@user.com')
        self.assertEqual(user.username, 'simple_john')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_negative(self):
        User = get_user_model()

        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email='')
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='meep')
           
    def test_create_super_user_positive(self):
        admin_user = CustomUser.objects.create_superuser(
            email='super@user.com'
            , password='$up3rUs3r'
            , username='bossMan'
            )
        self.assertEqual(admin_user.email, 'super@user.com')
        self.assertEqual(admin_user.username, 'bossMan')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_password_validation(self):
        User = get_user_model()
        with self.assertRaises(ValidationError):
            User.objects.create_user(
                email='validation_password_user@user.com'
                , password='failed_password'
                , username='validation_user_man'
            )


class OneTimeTokenTest(TestCase):
    '''
    The following test case contains positive and negative test cases for the OneTimeToken.
    It tests to see if the token is generated with the correct user_id and purpose as well as the automatic fields.
    Further, it performs negative test cases. 
    '''
    def test_create_token_positive(self):
        #Create CustomUser
        user = CustomUser.objects.create_user(
            email='test@user.com'
            , password='M3ep!234'
            , username = 'simple_john'
            )

        #Generate one_time_token
        one_time_token = generate_one_time_token(user.id, OneTimeToken.Purpose.AUTH)
        
        self.assertEqual(one_time_token.user_id, user.id)
        self.assertEqual(one_time_token.purpose, 'AUTH')
        self.assertNotEqual(one_time_token.purpose, 'AUTHENTICATE')
        self.assertIsNotNone(one_time_token.token)
        self.assertIsNotNone(one_time_token.expires_at)

    def test_create_token_negative(self):
        '''
        
        '''
        #Create CustomUser
        user = CustomUser.objects.create_user(
            email='test@user.com'
            , password='M3ep!234'
            , username = 'simple_john'
            )
        
        with self.assertRaises(AttributeError):
            generate_one_time_token(user.id, OneTimeToken.Purpose.PASSWORD)       
        with self.assertRaises(ValueError):
            generate_one_time_token(2, OneTimeToken.Purpose.AUTH)
