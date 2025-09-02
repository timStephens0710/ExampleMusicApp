from django.test import TestCase
from django.contrib.messages import get_messages
from django.core import mail
from django.urls import reverse


from ..models import OneTimeToken, CustomUser
from ..common.utils import generate_one_time_token


class UserRegistrationTests(TestCase):
    '''
    This test case asses the functionality in the view, user_registration().

    It handles the following test cases:
        - Positive:
            - the user is redirected to the correct view.
            - the user receives an email with the subject 'Authentication Email'.
        - Negative:
            - the correct form error is displayed to the user.
            - the correct response code.
            - the authentication email is not sent.
    '''
    def setUp(self):
        self.valid_email = 'test@user.com'
        self.valid_password = 'Meep!234'
        self.valid_username = 'simple_john'
        self.failed_email = 'fail.com'

    def test_user_authentication_email_positive(self):
        url = reverse("user_registration")
        response = self.client.post(url, {
            'email': self.valid_email
            , 'username': self.valid_username
            , 'password1': self.valid_password
            , 'password2': self.valid_password
        })

        #Check the correct redirect
        self.assertRedirects(response, reverse("user_authentication"))

        #Check that authenticatoin email has been sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.valid_email, mail.outbox[0].to)
        self.assertIn("Authentication Email", mail.outbox[0].subject)

    def test_user_authentication_negative(self):
        url = reverse("user_registration")
        response = self.client.post(url, {
            'email': self.failed_email
            , 'username': self.valid_username
            , 'password1': self.valid_password
            , 'password2': self.valid_password
        })
        
        #Check form error message
        self.assertContains(response, "Enter a valid email address")

        #Check correct code
        self.assertEqual(response.status_code, 200)

        #Check that authenticatoin email has NOT been sent
        self.assertEqual(len(mail.outbox), 0)


class UserResetPasswordTests(TestCase):
    '''
    The following test case, tests the 'reset password' feature.

    Test cases:
        - Positive results, that is, the password is updated and teh user can loging
        - Negative test case:
            - Incorrect email address
    '''
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@user.com",
            password="OldPass!234",
            username="simple_john"
        )
        self.token = generate_one_time_token(self.user.id, OneTimeToken.Purpose.RESET_PASSWORD)

        self.new_password = 'Updated!234'
        self.failed_password = 'fail'
        self.failed_email = 'nonexistent@user.com'

    def test_user_reset_password_positive(self):
            url = reverse("user_reset_password", args=[self.user.id, self.token.token])

            response = self.client.post(url, {
                "new_password1": self.new_password,
                "new_password2": self.new_password,
            })
            #Check the correct redirect
            self.assertRedirects(response, reverse("user_success_reset_password"))

            self.user.refresh_from_db()
            self.assertTrue(self.user.check_password(self.new_password))

            #The Token should now be marked as used
            self.token.refresh_from_db()
            self.assertTrue(self.token.is_used)

        
    def test_user_reset_password_negative(self):
        '''
        Submits a password reset request with an incorrect email.
        '''
        url = reverse("user_forgotten_password")

        response = self.client.post(url, {
             'email': self.failed_email
        })

        #Check the correct redirect
        self.assertRedirects(response, reverse("user_forgotten_password"))

        # Check correct message is displayed
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("find" in str(m).lower() for m in messages))


class UserResendPasswordEmail(TestCase):
    '''
    The following test case looks at the view, 'check_your_email_password()'

    It handles the following:
        - Positive:
            - A new token is generated.
            - The original token is_active = False
            - The reset password email is sent again with subject 'Rest Password'
    '''
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@user.com",
            password="OldPass!234",
            username="simple_john"
        )
        self.token = generate_one_time_token(self.user.id, OneTimeToken.Purpose.RESET_PASSWORD)


    def test_resend_reset_password_email_positive(self):
        url = reverse("check_your_email_password", args=[self.user.id])

        self.client.post(url)

        #Original token now is_active = False
        self.token.refresh_from_db()
        self.assertFalse(self.token.is_active)

        #New token doesn't equal current token
        new_token = OneTimeToken.objects.filter(
                        user_id=self.user.id,
                        is_used=False,
                        is_active=True,
                        purpose=OneTimeToken.Purpose.RESET_PASSWORD
                        ).exclude(token=self.token.token).first()
        
        self.assertNotEqual(new_token.token, self.token)

        #Email is has been sent again
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user.email, mail.outbox[0].to)
        self.assertIn("Reset Password", mail.outbox[0].subject)