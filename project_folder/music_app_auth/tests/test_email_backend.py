from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate #Based on what I've specified in settings.py AUTHENTICATION_BACKENDS

from ..models import CustomUser
from ..src.custom_exceptions import *

class EmailBackendTests(TestCase):
    '''
    The following test class contains the following test cases:
        - User exists, email_verified == True, password matches = success 
        - User exists, email_verified == True, password incorrect = fail 
        - User exists, email_verified == False 
        - User does not exist
    '''
    def setUp(self):
        self.valid_email = 'test@user.com'
        self.valid_password = 'Meep!234'
        self.valid_username = 'simple_john'
        self.failed_password = 'fail'
        self.unverified_email = 'unverified@user.com'

    def test_user_login_positive(self):
        CustomUser.objects.create_user(
            email=self.valid_email
            , password=self.valid_password
            , username = self.valid_username
            , email_verified = True
            )

        authenticated_user = authenticate(
            request = None
            ,email = self.valid_email
            ,password = self.valid_password
            )
    
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user.email, self.valid_email)

    def test_incorrect_password(self):
        CustomUser.objects.create_user(
            email=self.valid_email
            , password=self.valid_password
            , username = self.valid_username
            , email_verified = True
            )
                
        with self.assertRaises(IncorrectPassword) as cm:
            authenticate(
                request = None
                ,email = self.valid_email
                ,password = self.failed_password
                )
        self.assertIn('password', str(cm.exception).lower())

    def test_unverified_user(self):
        CustomUser.objects.create_user(
            email=self.unverified_email
            , password=self.valid_password
            , username = self.valid_username
            , email_verified = False
            )

        with self.assertRaises(UnverifiedEmail) as cm:
            authenticate(
            request = None
            ,email = self.unverified_email
            ,password = self.valid_password
            )
        self.assertIn('verify', str(cm.exception).lower())


    def test_user_does_not_exist(self):
        with self.assertRaises(EmailNotFound) as cm:
            authenticate(
                request = None
                ,email = 'nonexistent_user@home.com'
                ,password = 'missing'
                )
        self.assertIn('email', str(cm.exception).lower())