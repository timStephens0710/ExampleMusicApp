from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db.models import Subquery
from django.utils import timezone


from .models import AppLogging, OneTimeToken, CustomUser
from .forms import RegistrationForm, LoginForm, ForgottenPasswordForm, ResetPasswordForm

from .src.django_error_utils import handle_django_error
from .src.custom_exceptions import *
from .common.utils import generate_one_time_token
from .common.send_email import send_and_log_email


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def home(request):
    context = {
        'title' : "Music App"
    }
    return render(request, "music_app_home.html", context)


def user_registration(request):
    '''
    This view allows the user to sign-up.
    Once they have completed the form, they will receieve an email with a link to authenticate their profile.
    '''
    #Initialise registrationForm
    user_registration_form = RegistrationForm()

    try:
        if request.method == 'POST':
            user_registration_form = RegistrationForm(request.POST)
            if user_registration_form.is_valid():
                new_user_record = user_registration_form.save(commit=False)
                new_user_record.save()
                user_id = new_user_record.id
                user_email = new_user_record.email
                username = new_user_record.username

                #Add logging
                log_text = f'User registration form submitted successfully'
                AppLogging.objects.create(user_id = user_id, log_text = log_text)

                #Get one time token for authentication email link
                token_object = generate_one_time_token(user_id=user_id, purpose=OneTimeToken.Purpose.AUTH)

                #Authentication url
                authentication_link = request.build_absolute_uri(
                    reverse('user_authentication_success', args = [user_id, token_object.token])
                )

                #set email context
                email_context = {
                    'authentication_link': authentication_link
                    , 'username': username
                }

                #Send authentication email
                send_and_log_email(
                    request = request
                    ,user_id = user_id
                    ,subject = 'Music_app Authentication Email'
                    ,body_template ='authentication_email.html'
                    ,email_context = email_context
                    ,recipient_list = [user_email]
                    ,log_text = 'Sending authentication email.'
                    )

                return HttpResponseRedirect(reverse('user_authentication', args=[user_id]))
            else: #Return form if the form is not valid
                user_registration_form 
                context = {
                        'title' : "Music App | Sign-Up"
                        ,'form': user_registration_form
                    }
                return render(request, 'user_registration.html', context = context)            

        context = {
                'title' : "Music App | Sign-Up"
                ,'form': user_registration_form
            }
        return render(request, 'user_registration.html', context = context)
    except Exception as e:
        context = {}
        additional_context = handle_django_error(e)
        context.update(additional_context)
        return render(request, 'error_page.html', context = context)
    

def user_authentication(request, user_id):
    '''
    This view follows after the user has completed the registration form.
    The page tells them to check their email in orde to authenticate their profile.
    If the user doesn't receive the email, they can click the 'resend' button.
    '''
    #Get relevant user instance via user_id
    user = CustomUser.objects.get_user_instance_by_id(user_id)
    username = user.username
    user_email = user.email

    if request.method == 'POST':
        log_text = f'{user.username} has requested a new authentications email.'
        AppLogging.objects.create(user_id = user_id, log_text = log_text)

        try:
            current_token = OneTimeToken.objects.get_token_instance_wout_token(
                user_id = user_id
                , purpose = OneTimeToken.Purpose.AUTH
            )

            #Set current token to is_active = False
            current_token.is_active = False
            current_token.save()
            log_text = f'The current token for {user.username} has been deactivated.'
            AppLogging.objects.create(user_id = user_id, log_text = log_text)    
        except OneTimeToken.DoesNotExist:
            pass
        except OneTimeToken.MultipleObjectsReturned:
            log_text = f'Multiple active tokens for AUTH have been returned current token for {user.username}.'
            AppLogging.objects.create(user_id = user_id, log_text = log_text)
            current_token = OneTimeToken.objects.filter(
                user_id = user_id
                , is_used = False
                , is_active = True
                , purpose = OneTimeToken.Purpose.AUTH
                ).update(is_active = False)
        
        #Generate new token
        token_object = generate_one_time_token(user_id=user_id, purpose=OneTimeToken.Purpose.AUTH)

        #Reset password url
        authentication_link = request.build_absolute_uri(
            reverse('user_authentication_success', args = [user_id, token_object.token])
        )

        #set email context
        email_context = {
            'authentication_link': authentication_link
            , 'username': username
            }

        #Send authentication email
        send_and_log_email(
            request = request
            ,user_id = user_id
            ,subject = 'Music_app Authentication Email'
            ,body_template ='authentication_email.html'
            ,email_context = email_context
            ,recipient_list = [user_email]
            ,log_text = 'Sending authentication email.'
            )

        context = {
            'title' : "Music App"
            ,'user_id': user_id
        }
        return render(request, "user_authentication.html", context)
    else:
        context = {
            'title' : "Music App"
            ,'user_id': user_id
        }
        return render(request, "user_authentication.html", context)


def user_authentication_success(request, user_id, token):
    '''
    This view follows after the user has clicked on the hyperlink from their authentication email
    Therefore successfully authenticating their profile.
    '''
    #retrieve token + Update is used to True
    one_time_token = OneTimeToken.objects.get_token_instance_with_token(
        token = token
        , user_id = user_id
        , purpose = OneTimeToken.Purpose.AUTH
        )
    if one_time_token: 
        one_time_token.is_used = True
        one_time_token.is_active = False
        one_time_token.save()

        try:
            #Update CustomUser model
            user = CustomUser.objects.get_user_instance_by_id(user_id)
            user.email_verified = True
            user.save()
        
            context = {
                'title' : "Music App"
            }
            return render(request, "user_authentication_success.html", context)
        except CustomUser.DoesNotExist:
            return render(request, 'error_page.html', {"message": 'User not found'})
    else:
        context = {
                'title' : "Music App"
                ,'user_id': user_id
                ,'message': 'This link is invalid or has expired.'
            }    
        return render(request, "user_authentication.html", context)


def user_login(request):
    '''
    This view allows the user to login with their e-mail and password.
    Note:
        - If the user provides the incorrect details or hasn't verified their email address a message will be displayed in the front-end.
    '''
    #Initialise the LoginForm
    user_login_form = LoginForm()

    if request.method == 'POST':
        user_login_form = LoginForm(request.POST)
        if user_login_form.is_valid():
            email = user_login_form.cleaned_data['email']
            password = user_login_form.cleaned_data['password']
            try:
                user = authenticate(
                request = request
                ,email = email
                ,password = password
            )
                login(request, user)
                messages.success(request, 'Welcome d*_*b OMG')
                return redirect('the_feed')
            except EmailNotFound as e:
                messages.error(request, e.message)
            except UnverifiedEmail as e:
                messages.error(request, e.message)
            except IncorrectPassword as e:
                messages.error(request, e.message)
            return redirect('user_login')
    else:
        context = {
            'form': user_login_form
        }
        return render(request, 'user_login.html', context = context)


@login_required
def the_feed(request):
    '''
    The following view displays the music feed to the user, only if they are logged in.
    Otherwise, they are redirected to the login screen.
        - This is specified in the settings.py file by the variable LOGIN_URL
    '''
    return render(request, 'the_feed.html')


def user_logout(request):
    '''
    This view displays the logout page if the user has successfully logged out.
    '''
    logout(request)
    context = {
        'title' : "Music App"
    }
    return render(request, "user_logout_success.html", context)


def user_forgotten_password(request):
    '''
    The following view allows the user to reset their password if forgotten.
    The user will need to provide their email address in order to receive a reset password link.

    Note:
        - If the email address provided is not found, a message will be displayed in the front-end. 
    '''
    #Initialise forgottenPasswordForm
    user_forgotten_password_form = ForgottenPasswordForm()

    if request.method == 'POST':
        user_forgotten_password_form = ForgottenPasswordForm(request.POST)
        if user_forgotten_password_form.is_valid():
            #Take the email submitted by the user
            user_email = user_forgotten_password_form.cleaned_data['email']
            try:
                #Get relevant user instance via email
                user = CustomUser.objects.get_user_instance_by_email(user_email)
                user_id = user.id
                username = user.username

                #Add logging top record that the token has been set to used as 
                log_text = f'{user.username} has requested a reset password email.'
                AppLogging.objects.create(user_id = user_id, log_text = log_text)


                #Generate one time for resetting password link
                token_object = generate_one_time_token(user_id=user_id, purpose=OneTimeToken.Purpose.RESET_PASSWORD)

                #Reset password url
                reset_password_link = request.build_absolute_uri(
                    reverse('user_reset_password', args = [user_id, token_object.token])
                )

                #set email context
                email_context = {
                    'reset_password_link': reset_password_link
                    ,'username': username
                    }

                #Send reset password email
                send_and_log_email(
                    request = request
                    ,user_id = user_id
                    ,subject = 'Music_app Reset Password'
                    ,body_template ='reset_password_email.html'
                    ,email_context = email_context
                    ,recipient_list = [user_email]
                    ,log_text = 'Sending reset password email.'
                    )
                
                return HttpResponseRedirect(reverse('check_your_email_password', args=[user_id]))
                
            except EmailNotFound as e:
                messages.error(request, e.message)
                return HttpResponseRedirect(reverse("user_forgotten_password"))
    else:
        context = {
            'form': user_forgotten_password_form
        }
        return render(request, 'user_forgotten_password.html', context = context)


def check_your_email_password(request, user_id):
    '''
    This view follows after the user has completed the forgotten password form.
    The page tells them to check their emails to get the reset password link.

    If the user doesn't receive the email, they can click the 'resend' button. 
    #TODO display successful message to the user if they want the email re-sent.
    '''
    #Get relevant user instance via user_id
    user = CustomUser.objects.get_user_instance_by_id(user_id)

    if request.method == 'POST':
        #Add logging top record that the token has been set to used as 
        log_text = f'{user.username} has requested a new reset password email.'
        AppLogging.objects.create(user_id = user_id, log_text = log_text)

        #Find current token user_id, is_used == False, is_active = True
        try:
            current_token = OneTimeToken.objects.get_token_instance_wout_token(
                user_id = user_id
                , purpose = OneTimeToken.Purpose.RESET_PASSWORD
                )

            #Set current token to is_active = False
            current_token.is_active = False
            current_token.save()
            log_text = f'The current token for {user.username} has been deactivated.'
            AppLogging.objects.create(user_id = user_id, log_text = log_text)
        except OneTimeToken.DoesNotExist:
            pass
        except OneTimeToken.MultipleObjectsReturned:
            log_text = f'Multiple active tokens for RESET_PASSWORD have been returned current token for {user.username}.'
            AppLogging.objects.create(user_id = user_id, log_text = log_text)
            current_token = OneTimeToken.objects.filter(
                user_id = user_id
                , is_used = False
                , is_active = True
                , purpose = OneTimeToken.Purpose.RESET_PASSWORD
                ).update(is_active = False)

        #Generate new token
        token_object = generate_one_time_token(user_id=user_id, purpose=OneTimeToken.Purpose.RESET_PASSWORD)

        #Reset password url
        reset_password_link = request.build_absolute_uri(
            reverse('user_reset_password', args = [user_id, token_object.token])
        )

        #set email context
        email_context = {
            'reset_password_link': reset_password_link
            ,'username': user.username
            }

        #Send authentication email
        send_and_log_email(
            request = request
            ,user_id = user_id
            ,subject = 'Music_app Reset Password'
            ,body_template ='reset_password_email.html'
            ,email_context = email_context
            ,recipient_list = [user.email]
            ,log_text = 'Sending reset password email.'
            )
                
        #Render the "check_your_email_for_password.html"
        context = {
                'title' : "Music App | Reset Password"
                ,'user_id': user_id
            }
                
        return render(request, 'check_your_email_for_password.html', context)
    else:
        #Render the "check_your_email_for_password.html"
        context = {
            'title' : "Music App"
            ,'user_id': user_id
        }
        return render(request, "check_your_email_for_password.html", context)
    

def user_reset_password(request, user_id, token):
    '''
    This view follows after the user has completed the forgotten password form.
    The page tells them to check their emails to get the reset password link.
    '''
    #Get relevant user
    user = CustomUser.objects.get_user_instance_by_id(user_id)

    #initialise ResetPasswordForm
    reset_password_form = ResetPasswordForm(user)
    
    if request.method == 'POST':
        reset_password_form = ResetPasswordForm(user, request.POST)
        if reset_password_form.is_valid():
            #Save the form in order to update the user's password
            reset_password_form.save()

            try:
                #retrieve token + Update is used to True
                one_time_token = OneTimeToken.objects.get_token_instance_with_token(
                    token = token
                    , user_id = user_id
                    , purpose = OneTimeToken.Purpose.RESET_PASSWORD
                    )
                one_time_token.is_used = True
                one_time_token.is_active = False
                one_time_token.save()

                #Add logging to keep track of user
                log_text = f'User has updated password successfully'
                AppLogging.objects.create(user_id = user_id, log_text = log_text)

                return HttpResponseRedirect(reverse(viewname='user_success_reset_password'))
            except OneTimeToken.DoesNotExist:
                return render(request, 'error_page.html')
        else:
            reset_password_form
            context = {
                    'title' : "Music App | Reset Password"
                    ,'form': reset_password_form
                }
            return render(request, 'reset_password.html', context = context)             
    context = {
            'title' : "Music App | Reset Password"
            ,'form': reset_password_form
        }
    return render(request, 'reset_password.html', context = context)

def user_success_reset_password(request):
    '''
    This view follows after the user has successfully reset their password.
    '''
    return render(request, "user_success_reset_password.html")