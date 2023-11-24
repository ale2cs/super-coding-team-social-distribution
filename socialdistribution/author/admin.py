from django.contrib import admin
from .models import Profile, Follower, FriendFollowRequest, SiteConfiguration
from .forms import SiteConfigurationForm

# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Follower)
admin.site.register(FriendFollowRequest)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ['user_approval_required']
    form = SiteConfigurationForm
    actions = None
admin.site.register(SiteConfiguration, SiteConfigurationAdmin)