from django.shortcuts import render
from author.models import Follower, Profile, FriendFollowRequest
from inbox.models import Inbox
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

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
            if action == "unfollow":
                user_follow.following.remove(profile)
                inbox.follows.remove(profile)
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
    inbox = Inbox.objects.get(user=user_profile)
    likes = inbox.get_likes()
    comments = inbox.get_comments()
    follows = inbox.get_follows()
    requests = inbox.get_requests()
    return render(request, 'inbox.html', {'likes':likes, 'comments':comments, 'follows':follows, 'requests':requests})