from django.contrib import admin
from .models import Profile, Post, Follower, FriendFollowRequest, Image, Like
# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Post)
admin.site.register(Follower)
admin.site.register(FriendFollowRequest)
admin.site.register(Image)
admin.site.register(Like)