# Standard library imports
import logging

# Third-party imports
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.shortcuts import render

from ..models import AppLogging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def send_and_log_email(request, user_id , body_template, recipient_list, email_context, log_text, subject):
    """
    Send an email to a list of recipients and log the email event in the database.

    Args:
        request: HttpRequest object representing the current request context.
        user_id: The user ID instance associated with the email.
        subject: The subject of the email to be sent.
        body_template: The path to the template used for generating the email's body.
        recipient_list: List of email addresses that will receive the email.
        email_context: Context dictionary to render the body template.
        log_text: Custom text to be included in the log record.

    Returns:
        The HttpResponse object rendered from 'error_page.html' in case of an exception.
        Otherwise, if the email is sent successfully, the function returns None.

    Raises:
        Exception: If any issue arises during the email sending process. Exceptions are logged.
    """
    try: 
        body = render_to_string(body_template, email_context)

        for recipient in recipient_list:
            email = EmailMessage(subject = subject
                                ,body = body
                                ,from_email = settings.EMAIL_FROM
                                ,to = [recipient]
                                )
            email.send()
        AppLogging.objects.create(user_id=user_id, log_text=log_text)
    except Exception as e:
        logger.exception(f'Email failed: {e}')
        return render(request, "error_page.html", {})
