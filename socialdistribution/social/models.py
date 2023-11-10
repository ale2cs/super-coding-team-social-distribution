import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.
class Profile(models.Model):
    id = models.CharField(default=uuid.uuid4, editable=False, primary_key=True, max_length=200)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    avatar = models.ImageField(default='default.jpg', upload_to='profile_images')
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username
   

class Post(models.Model):
    id = models.CharField(default=uuid.uuid4, editable=False, primary_key=True, max_length=200)
    title = models.CharField(max_length=200)
    source = models.CharField(max_length=200)
    origin = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    contentType = models.CharField(max_length=200)
    content = models.CharField(max_length=200)
    author = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name="posts",default=None)
    # categories - figure out how to store these
    # count - number of comments
    # comments - url to comments
    # comment - ForeignKey
    published = models.DateTimeField(default=timezone.now)
    visibility = models.CharField(max_length=10)
    unlisted = models.BooleanField(default=False)
    
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

class Like(models.Model):
    summary = models.CharField(max_length=200)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, blank=True, null=True, on_delete=models.CASCADE)
    object = models.CharField(max_length=200)

class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    published = models.DateTimeField(auto_now_add=True)
    contentType = models.CharField(max_length=200, default="text/plain")

class Liked(models.Model):
    likedPosts = models.ManyToManyField(Like, related_name="liked_posts", symmetrical=False, blank=True)

class Inbox(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='inbox_owner')
    likes = models.ManyToManyField(Like, related_name='rec_likes', symmetrical=False, blank=True)
    comments = models.ManyToManyField(Comment, related_name='rec_comments', symmetrical=False, blank=True)
    follows = models.ManyToManyField(Profile, related_name='rec_follows', symmetrical=False, blank=True)
    posts = models.ManyToManyField(Post, related_name='rec_posts', symmetrical=False, blank=True)

    def get_likes(self):
        """
        Returns list of likes the author received
        """
        try:
            likes = self.likes.all()
        except AttributeError:
            return []
        return likes
    
    def get_comments(self):
        """
        Returns list of comments the author received
        """
        try:
            comments = self.comments.all() 
        except AttributeError:
            return []
        return comments
    
    def get_follows(self):
        """
        Returns list of follows the author received
        """
        try:
            follows = self.user.rec_follows.all() 
        except AttributeError:
            return []
        return [follow.user for follow in follows]

class Image(models.Model):
    upload = models.ImageField(upload_to='uploads/')