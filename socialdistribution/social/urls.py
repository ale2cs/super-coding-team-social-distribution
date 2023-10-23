from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    #path('update_profile/', update_profile, name='update_profile'),
    path('register_profile/', views.register_profile.as_view(), name='register_profile'),
    path('profile/', views.profile, name='profile'),
    path('service/authors/<str:author_id>/posts/<str:post_id>', views.PostDetail.as_view(), name='post-detail'),
    path('service/authors/<str:author_id>/posts', views.PostList.as_view(), name='post-list')
]