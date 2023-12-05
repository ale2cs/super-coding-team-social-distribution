from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('view_post/<str:post_id>', views.view_post, name='view_post'),
    path('edit_post/<str:post_id>', views.edit_post, name='edit_post'),
    path('delete_post/<str:post_id>', views.delete_post, name='delete_post'),
    path('share_post/<str:post_id>/<int:friend_id>', views.share_post, name='share_post'),
    path('view_remote_post/<str:node>/<path:remote_post>', views.view_remote_post, name='view_remote_post'),
    path('share_remote_post/<str:node>/<path:remote_post>/<int:friend_id>', views.share_remote_post, name='share_remote_post'),
]