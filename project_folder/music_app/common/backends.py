from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from ..src.custom_exceptions import *

class EmailBackend(ModelBackend):
    '''
    The EmailBackend class allows the following:
        - Map the email field to username so that the user can login via their email.
        - Raises the following exceptions:
            - email not found
            - email not verified
            - incorrect password put in
        - The authenticate() function returns:
            - User object
            - Reason string 
        -  To retrieve a user object by their id, from the session after they have logged in.
            - Otherwise, a logged-in session won't be able to map user_id back our CustomUser model.
        
    Note:
        - The get_user_model() function will pull whatever User model we have sefined in the AUTH_USER_MODEL variable in settings.py
        - In the user_login() view, the authenticate function will
    '''
    def authenticate(self, request, username = None, password = None, **kwargs):        
        UserModel = get_user_model()

        email = kwargs.get('email', username)
        try:
            user = UserModel.objects.get(email=email.lower())
        except UserModel.DoesNotExist:
            raise EmailNotFound(None)
            
        if not user.email_verified:
            raise UnverifiedEmail(None)

        if user.check_password(password) == False:
            raise IncorrectPassword(None)
        
        return user
        
    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None