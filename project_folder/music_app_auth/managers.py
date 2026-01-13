from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _

from .src.custom_exceptions import EmailNotFound

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        #Import password validators from settings
        password_validation.validate_password(password, user)

        user.set_password(password) # Utilise Django's built-in password hasher
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)
    
    def get_user_instance_by_id(self, user_id):
        '''
        Retrieves an instance from the CustomUser model by the user id
        '''
        return self.get(pk=user_id)
    
    def get_user_instance_by_email(self, user_email):
        '''
        Retrieves an instance from the CustomUser model by the user's email address
        '''
        try:
            return self.get(email=user_email)
        except ObjectDoesNotExist:
            raise EmailNotFound(user=None)


class CustomOneTimeTokenManager(BaseUserManager):
    '''
    Manager for the OneTimeToken model.
    Provides convenience methods for retrieving tokens safely.    '''
    def get_token_instance_wout_token(self, user_id, purpose):
        '''
        Retrieves an instance from the OneTimeToken model without using the token,  for the purpose of updating the specific token after one of
        the following actions:
            - User authentication
            - Resetting password
        '''
        try:
            return self.get(
                user_id = user_id
                , is_used = False
                , is_active = True
                , purpose = purpose
                )
        except self.model.DoesNotExist:
            return None
        except self.model.MultipleObjectsReturned:
            return (
                self.filter(
                    user_id=user_id
                    , is_used=False
                    , is_active=True
                    , purpose=purpose
                ).first()
            )
        
    def get_token_instance_with_token(self, token, user_id, purpose):
        '''
        Retrieves an instance from the OneTimeToken model using the token, for the purpose of updating the specific token after one of
        the following actions:
            - User authentication
            - Resetting password
        '''
        try:
            return self.get(
                token = token
                , user_id = user_id
                , is_used = False
                , is_active = True
                , purpose = purpose
                )
        except self.model.DoesNotExist:
            return None
        except self.model.MultipleObjectsReturned:
            return (
                self.filter(
                    token = token
                    , user_id=user_id
                    , is_used=False
                    , is_active=True
                    , purpose=purpose
                ).first()
            )