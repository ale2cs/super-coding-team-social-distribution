from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('service/authors/<str:author_id>/posts/<str:post_id>', views.PostDetail.as_view(), name='post-detail'),
    path('service/authors/<str:author_id>/posts', views.PostList.as_view(), name='post-list')
]