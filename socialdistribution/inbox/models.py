from django.db import models

# Create your models here.
class Inbox(models.Model):
    user = models.ForeignKey('author.Profile', on_delete=models.CASCADE, related_name='inbox_owner')
    likes = models.ManyToManyField('post.Like', related_name='rec_likes', symmetrical=False, blank=True)
    comments = models.ManyToManyField('post.Comment', related_name='rec_comments', symmetrical=False, blank=True)
    follows = models.ManyToManyField('author.Profile', related_name='rec_follows', symmetrical=False, blank=True)
    posts = models.ManyToManyField('post.Post', related_name='rec_posts', symmetrical=False, blank=True)
    requests = models.ManyToManyField('author.FriendFollowRequest', related_name='rec_requests', symmetrical=False, blank=True)

    def get_likes(self):
        """
        Returns list of likes the author received
        """
        try:
            likes = self.likes.all()
        except AttributeError:
            return []
        return likes
    
    def get_comments(self):
        """
        Returns list of comments the author received
        """
        try:
            comments = self.comments.all() 
        except AttributeError:
            return []
        return comments
    
    def get_follows(self):
        """
        Returns list of follows the author received
        """
        try:
            follows = self.user.rec_follows.all() 
        except AttributeError:
            return []
        return [follow.user for follow in follows]
    
    def get_requests(self):
        """
        Returns list of friend requests to the author
        """
        try:
            requests = self.requests.all() 
        except AttributeError:
            return []
        return requests
    
    def get_posts(self):
        try:
            posts = self.posts.all().order_by("-published")
        except AttributeError:
            return []
        return posts