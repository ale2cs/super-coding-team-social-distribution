import uuid
from django.db import models
from django.utils import timezone

# Create your models here.
class Author(models.Model):
    host = models.CharField(max_length=200)
    display =  models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    github = models.CharField(max_length=200)
    profile_image = models.IntegerField()

class Post(models.Model):
    id = models.CharField(default=uuid.uuid4, editable=False, primary_key=True, max_length=200)
    title = models.CharField(max_length=200)
    source = models.CharField(max_length=200)
    origin = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    contentType = models.CharField(max_length=200)
    content = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.CASCADE, related_name="posts")
    # categories - figure out how to store these
    # count - number of comments
    # comments - url to comments
    # comment - ForeignKey
    published = models.DateTimeField(default=timezone.now)
    visibility = models.CharField(max_length=10)
    unlisted = models.BooleanField(default=False)
    
class Follower(models.Model):
    host = models.CharField(max_length=200)
    display =  models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    github = models.CharField(max_length=200)
    profile_image = models.IntegerField()

