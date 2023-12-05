from django.contrib import admin
from .models import Post, Like, Comment, Image, Category, CommentLike, RemoteComment, RemoteLike, RemotePost

# Register your models here.
admin.site.register(Post)
admin.site.register(Image)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(CommentLike)
admin.site.register(RemoteComment)
admin.site.register(RemoteLike)
admin.site.register(RemotePost)
