"""
URL configuration for mysite project.

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
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    path('admin/', admin.site.urls)
    ,path('profile/<str:username>/', views.user_profile, name = 'user_profile')
    ,path('<str:username>/your_playlists/', views.user_playlists, name = 'user_playlists') #display of all the user's playlists
    ,path('<str:username>/create_playlist/', views.create_playlist, name = 'create_playlist') #create or update playlist
    ,path('<str:username>/<str:playlist_name>/', views.view_edit_playlist, name = 'view_edit_playlist') #view specific playlist
    ,path('<str:username>/<str:playlist_name>/add_link_to_track', views.add_streaming_link_to_playlist, name = 'add_streaming_link_to_playlist') #add track to a specific playlist
    ,path('<str:username>/<str:playlist_name>/add_track', views.add_track_to_playlist, name = 'add_track_to_playlist') #add track to a specific playlist

]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)