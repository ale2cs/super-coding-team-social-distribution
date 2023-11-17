from django.db import models

# Create your models here.
class Node(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    use_authentication = models.BooleanField(default=False)