"""
URL configuration for music_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import main_views, app_views

urlpatterns = [
    path('admin_tools_stats/', include('admin_tools_stats.urls'))
    , path('admin/', admin.site.urls)
    , path('', main_views.home, name = "music_app_home")
    , path('registration/', main_views.user_registration, name = "user_registration")
    , path('login/', main_views.user_login, name = 'user_login')
    , path('user_authentication/<int:user_id>/', main_views.user_authentication, name = "user_authentication")
    , path('user_authentication_success/<int:user_id>/<uuid:token>/', main_views.user_authentication_success, name = "user_authentication_success")
    , path('the_feed/', app_views.the_feed, name = "the_feed")
    , path('logout/', main_views.user_logout, name = "user_logout")
    , path('user_forgotten_password/', main_views.user_forgotten_password, name = 'user_forgotten_password')
    , path('check_your_email_password/<int:user_id>/', main_views.check_your_email_password, name = 'check_your_email_password')
    , path('user_reset_password/<int:user_id>/<uuid:token>/', main_views.user_reset_password, name = 'user_reset_password')
    , path('success_reset_password/', main_views.user_success_reset_password, name = 'user_success_reset_password')
    # , path('profile/<str:username>/', app_views.user_profile, name = 'user_profile')


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
