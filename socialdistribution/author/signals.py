from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from inbox.models import Inbox, RemoteInbox
from .models import Profile, Follower

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        new_profile =  Profile.objects.create(user=instance)
        Follower.objects.create(profile=new_profile)
        Inbox.objects.create(user=new_profile)
        RemoteInbox.objects.create(author=new_profile)
        

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()