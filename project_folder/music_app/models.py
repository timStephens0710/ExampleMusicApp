from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

import uuid

from .managers import CustomUserManager, CustomOneTimeTokenManager


class CustomUser(AbstractUser):
    '''
    This model stores the relavant data related to all users.

    It leverages off of the standard Django User model class, with the following custom changes:
        - Added field: email_verified.
        - Validate the user's email address.
        - Setting the email as the unique identifier for a user, as oppose to Django's default, username.
            - Refer to CustomUserManager in managers.py for further details.
        - Setting 'username' to a required field.
    '''
    #Remove unused built-in fields
    first_name = None
    last_name = None

    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(max_length=150, unique=True, blank = False)
    email_verified = models.BooleanField(default=False, validators=[validate_email])

    # Set email as the login field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    #Pull through the manager
    objects = CustomUserManager()

    def __str__(self):
        return self.username
    

class AppLogging(models.Model):
    '''
    Contains all of the logging information for procedures in the app.
    '''
    user = models.ForeignKey(to='CustomUser', on_delete=models.CASCADE, verbose_name='user_id')
    timestamp = models.DateTimeField(auto_now_add=True)
    log_text = models.TextField(blank=False, null=False)

    class Meta:
        ordering = ['user', '-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp'],
                         name='AppLoggingIdx')
        ]


class OneTimeToken(models.Model):
    '''
    This model contains the one time tokens that are used for the following puporses:
        - The user authentication their profile
        - The user resetting their password
        - The user wants to collaborate with other user(s) on a playlist
    '''
    class Purpose(models.TextChoices):
        AUTH = ('AUTH', 'User authentication')
        RESET_PASSWORD = ('RESET_PASSWORD', 'Reset user password')
        COLLAB_PLAYLIST = ('COLLAB_PLAYLIST', 'Playlist collaboration')

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(to='CustomUser', on_delete=models.CASCADE, verbose_name='user_id')
    purpose = models.CharField(choices=Purpose.choices, max_length = 50, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=False, null=False)
    is_used = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    #Pull through the manager
    objects = CustomOneTimeTokenManager()
