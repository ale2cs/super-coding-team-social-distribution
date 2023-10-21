from django import views
from django.urls import path
from .views import home_page, register_profile, profile

urlpatterns = [
    path('', home_page, name='home'),
    #path('update_profile/', update_profile, name='update_profile'),
    path('register_profile/', register_profile.as_view(), name='register_profile'),
    path('profile/', profile, name='profile'),

]