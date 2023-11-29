from django.urls import path
from . import views

urlpatterns = [
    #path('update_profile/', update_profile, name='update_profile'),
    path('register_profile/', views.register_profile.as_view(), name='register_profile'),
    path('change_password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('profile/', views.profile, name='profile'),
    path('friends/', views.friends_list, name='friends'),
    path('social/', views.profile_list, name='social'),
    path('social/<int:pk>', views.profile_detail, name='profile_detail'),
    path('social/follow/<str:node>/<path:remote_author>', views.send_remote_follow, name='send_remote_follow'),
    path('respond_to_follow_request/<int:friend_request_id>/<str:action>/', views.respond_to_follow_request, name='respond_to_follow_request'),
    path('respond_to_remote_follow_request/<int:remote_friend_request_id>/<str:action>/', views.respond_to_remote_follow_request, name='respond_to_remote_follow_request'),
    path('social/unfollow/<str:node>/<path:remote_author>', views.send_remote_unfollow, name='send_remote_unfollow')
]