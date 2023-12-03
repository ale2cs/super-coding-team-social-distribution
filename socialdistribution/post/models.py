import uuid
import base64
from itertools import chain
from operator import attrgetter
from django.db import models
from django.utils import timezone
from api.services import get_author_from_link

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
        remote_comments = RemoteComment.objects.filter(post=self)

        # get author displayName from all remote comments
        for remote_comment in remote_comments:
            remote_comment.author = get_author_from_link(remote_comment.author)['displayName']

        # Combine the two querysets
        all_comments = sorted(chain(comments, remote_comments), key=attrgetter('published'), reverse=True)

        return all_comments, len(all_comments)
    
    def get_likes(self):
        """
        Returns the number of likes on the post
        """
        likes = list(Like.objects.filter(post=self)) + list(RemoteLike.objects.filter(post=self))
        return len(likes)

class RemotePost(models.Model):
    post_id = models.CharField(max_length=300, default=None)



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

    def get_likes(self):
        """
        Returns the number of likes on the comment
        """

        likes = RemoteCommentLike.objects.filter(comment=self)
        return len(likes)
    
    def liked(self, liked_user):
        """
        Returns true if a comment is liked by liked_user
        false otherwise
        """

        data = RemoteCommentLike.objects.filter(comment=self, author=liked_user)
        if len(data) > 0:
            return True
        return False

class CommentLike(models.Model):
    summary = models.CharField(max_length=200)
    author = models.ForeignKey('author.Profile', on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, blank=True, null=True, on_delete=models.CASCADE)

class RemoteCommentLike(models.Model):
    summary = models.CharField(max_length=200)
    author = models.CharField(max_length=300)
    comment = models.ForeignKey('RemoteComment', blank=True, null=True, on_delete=models.CASCADE)


class Image(models.Model):
    upload = models.ImageField(upload_to='uploads/')