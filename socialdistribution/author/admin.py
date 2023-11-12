from django.contrib import admin

from .models import Profile, Follower, FriendFollowRequest

# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Follower)
admin.site.register(FriendFollowRequest)