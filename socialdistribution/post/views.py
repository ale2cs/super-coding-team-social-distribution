import json
from .models import Post, Like, Comment, CommentLike
from author.models import Follower, Profile
from inbox.models import Inbox
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CreatePostForm, CreateCommentForm

# Create your views here.
@login_required
def home_page(request):
    if request.user.is_authenticated:
        follow = Follower.objects.get(profile=request.user.profile)
        friends = follow.get_friends()
        own_post = Q(author=request.user.profile)
        is_public = Q(Q(visibility="public"), Q(unlisted=False))
        is_friend_post = Q(Q(visibility="friends"), Q(author__in=friends))
        posts = Post.objects.all().filter(own_post | is_public | is_friend_post).order_by("-published")
        
        if request.method == "POST":
            form = CreatePostForm(request.POST, request.FILES)
            action = request.POST['post']
            if action == "create_post":
                if form.is_valid():
                    post = form.save(commit=False)
                    post.author = request.user.profile
                    post.save()
                    messages.success(request, ("Post created successfully!"))
                    
                    if post.visibility == "public":
                        for follower in follow.get_followers():
                            inbox = Inbox.objects.get(user=follower)
                            inbox.posts.add(post)
                    elif post.visibility == "friends":
                        for friend in follow.get_friends():
                            inbox = Inbox.objects.get(user=friend)
                            inbox.posts.add(post)
                    return redirect('home')
        else:
            form = CreatePostForm()
        return render(request, 'home.html', {"posts":posts, "form":form})


def post_like(request, pk):
    if request.user.is_authenticated:
        if request.method == "POST":
            desc = request.user.username + " Likes your post"
            Like.objects.create(summary=desc, author=request.user.profile, post=pk)
            messages.success(request, ("You have liked the post!"))
            return redirect('home')
    else:
        messages.success(request, ("You must be logged in to like a post."))
        return redirect('home')
        
def edit_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.method == "POST":
        form = CreatePostForm(request.POST or None, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user.profile
            post.save()
            messages.success(request, ("Post updated successfully!"))
            return redirect('home')
    else:
        form = CreatePostForm(instance=post)
    return render(request, 'update_post.html', {"post": post, "form": form})
    
def delete_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.method == "POST":
        post.delete()
        messages.success(request, ("Post deleted successfully!"))
        return redirect('home')
    return render(request, "delete_post.html", {"post": post})

@login_required
def view_post(request, post_id):

    # get friends
    follow = Follower.objects.get(profile=request.user.profile)
    friends = follow.get_friends()

    # get likes
    postGet = Post.objects.get(id=post_id)
    likedUser = request.user.profile
    #likePosts = Like.objects.filter(post=postGet)
    likes = postGet.get_likes()

    # access post author's inbox
    inbox = Inbox.objects.get(user=postGet.author.user.profile)

    # get comments
    comments, commentCount = postGet.get_comments()

    commentsInfo = []
    index = 0
    for comment in comments:
        commentLikes = comment.get_likes()
        isLiked = comment.liked(likedUser)
        commentsInfo.append([comment, commentLikes, isLiked, index])
        index += 1

    # get like/unlike button for post
    liked = True
    data = Like.objects.filter(post=postGet, author=likedUser)
    if len(data) > 0:
        liked = True
    else:
        liked = False
    
    # get comment form
    form = CreateCommentForm(request.POST or None)

    if request.method == "POST":
        action = request.POST['action']
        # print(action)
        if action == "like":
            likeSummary = likedUser.user.username + " liked your post!"
            like = Like(summary=likeSummary,author=likedUser, post=postGet) 
            like.save()
            inbox.likes.add(like)
            messages.success(request, ("Post Liked successfully!"))
        elif action == "unlike":
            like = Like.objects.filter(post=postGet, author=likedUser).delete()
            messages.success(request, ("Post unliked successfully!"))
        elif action == "comment":
            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = request.user.profile
                comment.post = postGet
                comment.save()
                inbox.comments.add(comment)
                messages.success(request, ("Commented on post successfully!"))
        elif "," in action:
            commentAction = action.split(",")
            commentLiking = commentAction[0]
            commentIndex = int(commentAction[1])
            if commentLiking == "like":
                likeSummary = likedUser.user.username + " liked your comment!"
                like = CommentLike(summary=likeSummary, author=likedUser,comment=commentsInfo[commentIndex][0])
                like.save()
                messages.success(request, ("Comment Liked successfully!"))
                # inbox?
            elif commentLiking == "unlike":
                like = CommentLike.objects.filter(author=likedUser,comment=commentsInfo[commentIndex][0]).delete()
                messages.success(request, ("Comment Unliked successfully!"))
                # inbox?

        inbox.save()
        return redirect("home")
    return render(request, "view_post.html", {"post":postGet, "likes":likes, "liked":liked, "commentsInfo":commentsInfo, "commentCount":commentCount, "form": form, "friends":friends})

@login_required
def share_post(request, post_id, friend_id):
    profile = Profile.objects.get(user_id=friend_id)
    inbox = Inbox.objects.get(user=profile)
    post = Post.objects.get(id=post_id)

    if request.method == "POST":
        action = request.POST['confirm']
        if action == "yes":
            inbox.posts.add(post)
        inbox.save()
        return redirect("view_post", post_id)
    return render(request, "share_post.html", {'shared_posts':inbox.get_posts(), 'post':post})

