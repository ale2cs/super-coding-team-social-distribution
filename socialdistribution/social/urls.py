from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    #path('update_profile/', update_profile, name='update_profile'),
    path('register_profile/', views.register_profile.as_view(), name='register_profile'),
    path('change_password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('profile/', views.profile, name='profile'),
    path('social/', views.SocialView.as_view(), name='social'),
    path('social/<str:pk>/author', views.ProfileView.as_view(), name='profile-detail'),
    path('service/authors/<str:author_id>/posts/<str:post_id>', views.PostDetail.as_view(), name='post-detail'),
    path('service/authors/<str:author_id>/posts', views.PostList.as_view(), name='post-list'),
    path('service/authors/<str:author_id>/followers', views.Followers.as_view(), name='followers'),
]