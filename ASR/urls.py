from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import (
    settings, notifications_settings, sign_in, sign_up, profile, telega_book, 
    telega_fetch, check_schedule, book, telega_auth, telega_fetch_rooms
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('social-auth/', include('social_django.urls', namespace="social")),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('notifications_settings', notifications_settings,
         name='notifications_settings'),
    path('profile', profile, name='profile'),
    path('settings', settings, name='settings'),
    path('sign_in', sign_in, name='sign_in'),
    path('sign_up', sign_up, name='sign_up'),
    path('MainApp/', include('MainApp.urls')),
    
    path('ajax/check_schedule', check_schedule, name='check_schedule'),
    path('ajax/book', book, name='book'),

    path('telega/auth',telega_auth),
    path('telega/book', telega_book),
    path('telega/fetch', telega_fetch),
    path('telega/fetch/rooms', telega_fetch_rooms),
]
