from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db.models import Subquery
from django.utils import timezone


from ..src.custom_exceptions import *


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def home(request):
    context = {
        'title' : "Music App"
    }
    return render(request, "music_app_home.html", context)


@login_required
def the_feed(request):
    '''
    The following view displays the music feed to the user, only if they are logged in.
    Otherwise, they are redirected to the login screen.
        - This is specified in the settings.py file by the variable LOGIN_URL
    '''
    return render(request, 'the_feed.html')

