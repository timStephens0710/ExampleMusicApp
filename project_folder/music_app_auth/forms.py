from django import forms
from django.core import exceptions
from django.forms import ModelForm
from django.contrib.auth import password_validation
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    '''
    The following form is used as a template to create a new CustomUser
    '''
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
            "is_staff",
            "is_superuser",
            "is_active",
        )


class CustomUserChangeForm(UserChangeForm):
    '''
    The following form is used for updating fields for a current user.
    For list of fields that can be updated erfer to the 'fields' variable below.
    '''
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
            "is_staff",
            "is_superuser",
            "is_active",
            "email_verified",
        )

class RegistrationForm(CustomUserCreationForm):
    '''
    The sign-up form for the user.
    By setting both the password1 & password2 fields to 'data-password' the JS file show_password will function dynamically.
    '''
    password1 = forms.CharField(
            label = 'Password (8 characters minimum)'
            , widget=forms.PasswordInput(attrs={
                'class': 'form-control'
                ,'data-password': 'true'  
                
            })
        )
    password2 = forms.CharField(
            label = 'Confirm password'
            , widget=forms.PasswordInput(attrs={
                'class': 'form-control'
                ,'data-password': 'true'  
                
            })
        )
    class Meta(CustomUserCreationForm.Meta):
        model = CustomUser
        fields = ['email', 'username', 'password1', 'password2']
        labels = {
            'email': 'Your email address',
            'username': 'Username'
        }


class LoginForm(forms.Form):
    '''
    The login form.
    Note:
        - We do not need to reference the CustomUser model as we're not creating a user,
        we're simply just capturing the login details.
    '''
    email = forms.CharField(max_length=100, widget=forms.EmailInput(attrs={
        'class': 'auth-form-input'
    })
    )
    password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'auth-form-input'
        ,'data-password': 'true'
    })
    )


class ForgottenPasswordForm(forms.Form):
    '''
    The user only needs to enter their email.
    '''
    email = forms.CharField(max_length=100, label='Please enter your email address')


class ResetPasswordForm(SetPasswordForm):
    '''
    A form that lets a user set their password without entering the old
    password.
    '''
    new_password1 = forms.CharField(
            label = 'New password (8 characters minimum)'
            , widget=forms.PasswordInput(attrs={
                'class': 'form-control'
                ,'data-password': 'true'  
                
            })
        )
    new_password2 = forms.CharField(
            label = 'Confirm new password'
            , widget=forms.PasswordInput(attrs={
                'class': 'form-control'
                ,'data-password': 'true'  
                
            })
        )
    class Meta:
        model = CustomUser
        fields = ['new_password1', 'new_password2']