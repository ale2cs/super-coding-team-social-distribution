from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('view_post/<str:post_id>', views.view_post, name='view_post'),
    path('edit_post/<str:post_id>', views.edit_post, name='edit_post'),
    path('delete_post/<str:post_id>', views.delete_post, name='delete_post'),
]