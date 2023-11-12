import json
from .models import Post, Like, Comment
from author.models import Follower
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
        
        form = CreatePostForm(request.POST or None)
        if request.method == "POST":
            action = request.POST['post']
            if action == "create_post":
                if form.is_valid():
                    post = form.save(commit=False)
                    post.author = request.user.profile
                    post.save()
                    messages.success(request, ("Post created successfully!"))
                    return redirect('home')
        return render(request, 'home.html', {"posts":posts, "form":form})

    posts = Post.objects.all().order_by("-published")
    return render(request, 'home.html', {"posts":posts})

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
    form = CreatePostForm(request.POST or None, instance=post)
    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user.profile
            post.save()
            messages.success(request, ("Post updated successfully!"))
            return redirect('home')
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

    # get likes
    postGet = Post.objects.get(id=post_id)
    likedUser = request.user.profile
    likePosts = Like.objects.filter(post=postGet)
    likes = len(likePosts)

    # access post author's inbox
    inbox = Inbox.objects.get(user=postGet.author.user.profile)

    # get comments
    comments = Comment.objects.filter(post=postGet).order_by("-published")
    commentCount = len(comments)

    # get like/unlike button
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
        if action == "like":
            likeSummary = likedUser.user.username + " liked your post!"
            like = Like(summary=likeSummary,author=likedUser, post=postGet, object="")    
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
        inbox.save()
        return redirect("home")
    return render(request, "view_post.html", {"post":postGet, "likes":likes, "liked":liked, "comments":comments, "commentCount":commentCount, "form": form})

