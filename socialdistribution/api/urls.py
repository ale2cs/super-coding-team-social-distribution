from django.urls import path
from . import views

urlpatterns = [
    path('authors', views.Authors.as_view(), name='authors-list'),
    path('authors/<str:author_id>', views.Author.as_view(), name='single-author'),
    path('authors/<str:author_id>/posts', views.PostList.as_view(), name='post-list'),
    path('authors/<str:author_id>/posts/<str:post_id>', views.PostDetail.as_view(), name='post-detail'),
    path('authors/<str:author_id>/posts/<str:post_id>/comments', views.Comments.as_view(), name='comment'),
    path('authors/<str:author_id>/followers', views.Followers.as_view(), name='followers'),
    path('authors/<str:author_id>/followers/<str:foreign_author_id>', views.FollowersAction.as_view(), name='followers-action'),
    path('authors/<str:author_id>/liked', views.LikedPosts.as_view(), name='liked-list'),
    path('authors/<str:author_id>/posts/<str:post_id>/likes', views.LikesOnPost.as_view(), name='likes-on-post'),
    path('authors/<str:author_id>/posts/<str:post_id>/comments/<str:comment_id>/likes', views.LikesOnComment.as_view(), name='likes-on-comment'),
    path('authors/<str:author_id>/inbox', views.InboxAdd.as_view(), name='inbox'),
]