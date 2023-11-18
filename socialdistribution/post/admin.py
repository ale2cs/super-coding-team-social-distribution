from django.contrib import admin
from .models import Post, Like, Comment, Image, Category

# Register your models here.
admin.site.register(Post)
admin.site.register(Image)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Category)