from django.urls import path
from . import views

urlpatterns = [
    path('service/authors/<str:author_id>/posts/<str:post_id>', views.PostDetail.as_view(), name='post-detail'),
    path('service/authors/<str:author_id>/posts', views.PostList.as_view(), name='post-list'),
    path('service/authors/<str:author_id>/followers', views.Followers.as_view(), name='followers'),
    path('service/authors/<str:author_id>/followers/<str:foreign_author_id>', views.FollowersAction.as_view(), name='followers-action'),
]