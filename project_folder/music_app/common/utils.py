from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist

from ..models import OneTimeToken, AppLogging, CustomUser

def generate_one_time_token(user_id, purpose):
    '''
    This function generates a one-time token that will be used for a specific purpose.

    It calls the model OneTimeToken, and asigns the following:
        - A token
        - An expiration time
        - A specific user_id
        - A specific purpose.
    '''
    #Check the user exists first before inserting into the DB
    try:
        user = CustomUser.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        raise ValueError(f'User with {user_id} does not exist.')

    #Set expiration time
    expiration_time = timezone.now() + timedelta(hours=1)

    #Create one_time_token object via OneTimeToken
    one_time_token = OneTimeToken.objects.create(
        user_id = user.id
        ,purpose = purpose
        ,expires_at = expiration_time
    )

    #Add logging to save putting it in the views etc.
    log_text = 'One time token has been generated'
    AppLogging.objects.create(user_id = user.id, log_text = log_text)

    return one_time_token

