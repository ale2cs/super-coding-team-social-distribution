from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('inbox/<int:pk>', views.inbox_request, name='inbox_request'),
]