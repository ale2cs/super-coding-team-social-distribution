from django.contrib import admin
from social.models import Author, Post, Follower

# Register your models here.
admin.site.register(Author)
admin.site.register(Post)
admin.site.register(Follower)
