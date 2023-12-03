from django.shortcuts import render
from author.models import Follower, Profile, FriendFollowRequest
from inbox.models import Inbox, RemoteInbox
from post.models import Post
from api.services import get_author_from_link
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from urllib.parse import urlparse
from author import services

# Create your views here.
@login_required
def inbox_request(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        follow = Follower.objects.get(profile=profile)
        user_profile = request.user.profile
        inbox = Inbox.objects.get(user=user_profile)
        user_follow = Follower.objects.get(profile=user_profile)           

        # Post form logic
        if request.method == "POST":
            action = request.POST['accept']
            if action == "decline":
                FriendFollowRequest.objects.filter(follower=profile, followee=user_profile).delete()
            elif action == "accept":
                user_follow.following.add(profile)
                inbox.follows.add(profile)
                FriendFollowRequest.objects.filter(follower=profile, followee=user_profile).delete()
            user_follow.save()
            return redirect("inbox")
        return render(request, 'inbox_request.html', {'profile':profile, 'follow':follow, 'user_follow':user_follow})

@login_required
def inbox(request):
    user_profile = request.user.profile

    # remote
    remote_inbox = RemoteInbox.objects.get(author=user_profile)
    remote_likes = list(remote_inbox.likes.all())
    remote_comments = list(remote_inbox.comments.all())
    remote_posts = list(remote_inbox.comments.all())
    remote_requests = (remote_inbox.requests.all())
    for remote_comment in remote_comments:
        remote_comment.author = get_author_from_link(remote_comment.author)['displayName']
    for remote_post in remote_posts:
        remote_post.author = get_author_from_link(remote_post.author)['displayName']

    # local
    inbox = Inbox.objects.get(user=user_profile)
    likes = list(inbox.get_likes()) + remote_likes
    comments = list(inbox.get_comments()) + remote_comments
    posts = list(inbox.get_posts()) + remote_posts
    follows = inbox.get_follows()
    requests = inbox.get_requests()
    comment_likes = inbox.get_comment_likes()
    # remote_items = remote_inbox.items

    # if remote_items != None:
    #     for item in remote_items:
    #         if item['type'].lower() == 'like':
    #             item['post'] = {}
    #             item['post']['id']= item['object'].split('/')[-1]
    #             likes.append(item)
    #         elif item['type'].lower() == 'comment':
    #             url_parts = item['id'].split('/')
    #             item['post'] = {}
    #             item['post']['id'] = url_parts[url_parts.index('posts') + 1]
    #             item['author'] = item['author']['displayName']
    #             comments.append(item)
    #         elif item['type'].lower() == 'post':
    #             posts.append(item)
                
    return render(request, 'inbox.html', {
        'likes':likes, 
        'comments':comments, 
        'follows':follows, 
        'requests':requests, 
        'posts':posts, 
        'comment_likes':comment_likes,
        'remote_requests':remote_requests,
    })