import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    avatar = models.ImageField(default='default.jpg', upload_to='profile_images')
    bio = models.TextField()

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
    host = models.CharField(max_length=200)
    display =  models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    github = models.CharField(max_length=200)
    profile_image = models.IntegerField()

