import uuid
from django.db import models
from django.utils import timezone

# Create your models here.
class Post(models.Model):
    id = models.CharField(default=uuid.uuid4, editable=False, primary_key=True, max_length=200)
    title = models.CharField(max_length=200)
    source = models.CharField(max_length=200)
    origin = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    contentType = models.CharField(max_length=200)
    content = models.CharField(max_length=200)
    author = models.ForeignKey('author.Profile', on_delete=models.CASCADE, related_name="posts",default=None)
    # categories - figure out how to store these
    # count - number of comments
    # comments - url to comments
    # comment - ForeignKey
    published = models.DateTimeField(default=timezone.now)
    visibility = models.CharField(max_length=10)
    unlisted = models.BooleanField(default=False)
    
class Like(models.Model):
    summary = models.CharField(max_length=200)
    author = models.ForeignKey('author.Profile', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, blank=True, null=True, on_delete=models.CASCADE)
    object = models.CharField(max_length=200)

class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey('author.Profile', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    published = models.DateTimeField(auto_now_add=True)
    contentType = models.CharField(max_length=200, default="text/plain")

class Liked(models.Model):
    likedPosts = models.ManyToManyField(Like, related_name="liked_posts", symmetrical=False, blank=True)

class Image(models.Model):
    upload = models.ImageField(upload_to='uploads/')