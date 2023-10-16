from django.db import models

# Create your models here.
class Author(models.Model):
    author_id = models.CharField(max_length=200)
    host = models.CharField(max_length=200)
    display =  models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    github = models.CharField(max_length=200)
    profile_image = models.IntegerField()

class Post(models.Model):
    post_id = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    source = models.CharField(max_length=200)
    origin = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    content_type = models.CharField(max_length=200)

class Follower(models.Model):
    follower_id = models.CharField(max_length=200)
    host = models.CharField(max_length=200)
    display =  models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    github = models.CharField(max_length=200)
    profile_image = models.IntegerField()

