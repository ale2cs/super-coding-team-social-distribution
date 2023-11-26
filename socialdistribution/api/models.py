from django.db import models

# Create your models here.
class Node(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    outbound_username = models.CharField(max_length=200, null=True)
    outbound_password = models.CharField(max_length=200, null=True)
    use_authentication = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.url)
