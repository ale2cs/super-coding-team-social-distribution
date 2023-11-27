from django.contrib import admin
from .models import Inbox, RemoteInbox, RemoteInboxItem

# Register your models here.
admin.site.register(Inbox)
admin.site.register(RemoteInbox)
admin.site.register(RemoteInboxItem)