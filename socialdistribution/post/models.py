import uuid
import base64
from django.db import models
from django.utils import timezone

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
class Post(models.Model):
    id = models.CharField(default=uuid.uuid4, editable=False, primary_key=True, max_length=200)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=10000)
    contentType = models.CharField(max_length=200)
    content = models.CharField(max_length=200)
    author = models.ForeignKey('author.Profile', on_delete=models.CASCADE, related_name="posts",default=None)
    categories = models.ManyToManyField(Category)
    published = models.DateTimeField(default=timezone.now)
    visibility = models.CharField(max_length=10)
    unlisted = models.BooleanField(default=False)
    image_url = models.URLField(max_length=200, blank=True, null=True)
    image_file = models.FileField(upload_to="uploads", blank=True, null=True)

    def get_comments(self):
        """
        Returns list of comments on the post ordered by date it was published, 
        as well as returns the number of comments on the post,
        """
        comments = Comment.objects.filter(post=self).order_by("-published")
        return comments, len(comments)
    
    def get_likes(self):
        """
        Returns the number of likes on the post
        """
        likes = Like.objects.filter(post=self)
        return len(likes)

class Like(models.Model):
    summary = models.CharField(max_length=200)
    author = models.ForeignKey('author.Profile', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, blank=True, null=True, on_delete=models.CASCADE)

class RemoteLike(models.Model):
    summary = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)


class Comment(models.Model):
    id = models.CharField(default=uuid.uuid4, editable=False, primary_key=True, max_length=200)
    content = models.TextField()
    author = models.ForeignKey('author.Profile', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    published = models.DateTimeField(auto_now_add=True)
    contentType = models.CharField(max_length=200)

    def get_likes(self):
        """
        Returns the number of likes on the comment
        """

        likes = CommentLike.objects.filter(comment=self)
        return len(likes)
    
    def liked(self, liked_user):
        """
        Returns true if a comment is liked by liked_user
        false otherwise
        """

        data = CommentLike.objects.filter(comment=self, author=liked_user)
        if len(data) > 0:
            return True
        return False

class RemoteComment(models.Model):
    id = models.CharField(default=uuid.uuid4, editable=False, primary_key=True, max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=200)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    published = models.DateTimeField(auto_now_add=True)
    contentType = models.CharField(max_length=200)

class CommentLike(models.Model):
    summary = models.CharField(max_length=200)
    author = models.ForeignKey('author.Profile', on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, blank=True, null=True, on_delete=models.CASCADE)

class Image(models.Model):
    upload = models.ImageField(upload_to='uploads/')