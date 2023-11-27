import uuid
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    id = models.CharField(default=uuid.uuid4, editable=False, primary_key=True, max_length=200)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    github = models.CharField(max_length=200)
    avatar = models.ImageField(default='default.jpg', upload_to='profile_images')
    bio = models.TextField(blank=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class FollowerRemote(models.Model):
    following_author = models.ForeignKey(Profile, on_delete=models.CASCADE, default=None)
    remote_id = models.CharField(max_length=300, default=None)

class Follower(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='profile')
    following = models.ManyToManyField(Profile, related_name='followed_by', symmetrical=False, blank=True)

    def get_followers(self):
        """
        Returns list of followers
        """
        try:
            follow = self.profile.followed_by.all() 
        except AttributeError:
            return []
        return [follower.profile for follower in follow]

    def get_friends(self):
        """
        Returns list of friends (bidirectional follow)

        """
        following = set(self.following.all())
        followers = set(self.get_followers())
        return list(following.intersection(followers))

class FriendFollowRequest(models.Model):
    summary = models.CharField(max_length=200)
    follower = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='follower')
    followee = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='followee')
    status = models.CharField(max_length=20, default='pending')
    def accept(self):
        self.status = 'accepted'
        self.save()

    def decline(self):
        self.status = 'declined'
        self.save()

class RemoteFriendFollowRequest(models.Model):
    summary = models.CharField(max_length=200)
    follower = models.CharField(max_length=300, default=None)
    followee = models.ForeignKey(Profile, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')
    def accept(self):
        self.status = 'accepted'
        self.save()

    def decline(self):
        self.status = 'declined'
        self.save()

class SiteConfiguration(models.Model):
    user_approval_required = models.BooleanField(default=True)
