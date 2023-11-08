import json
from django.db import IntegrityError, models
from django.db.models import Q
from rest_framework.views import APIView
from .models import Profile, Post, Follower, FriendFollowRequest, Like, Comment
from .serializers import ProfileSerializer, PostSerializer, FollowerSerializer, LikeSerializer, Comment
from rest_framework.response import Response
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View, generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import RegisterUser, LoginUser, UpdateUserForm, UpdateProfileForm, CreatePostForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404

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
            like = Likes.object()
            like.summary = request.user.username + " Likes your post"
            #like.author, need to figure out how to connect the liked post to the post author
            #like.object, need to figure out how to connect the liked post link to the like
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

class CustomLoginView(LoginView):
    form_class = LoginUser

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)
    
class register_profile(View):
    form_class = RegisterUser
    initial = {'key': 'value'}
    template_name = 'register_profile.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(register_profile, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect(to='/')

        return render(request, self.template_name, {'form': form})
    
class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('home')    

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'profile.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def profile_list(request):
    profiles = Profile.objects.exclude(user=request.user)
    return render(request, 'social.html', {"profiles":profiles})

@login_required
def profile_detail(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        follow = Follower.objects.get(profile=profile)
        user_profile = request.user.profile
        user_follow = Follower.objects.get(profile=user_profile)           

        # Post form logic
        if request.method == "POST":
            action = request.POST['follow']
            if action == "unfollow":
                user_follow.following.remove(profile)
            elif action == "follow":
                user_follow.following.add(profile)
            user_follow.save()

        return render(request, 'other_profiles.html', {'profile':profile, 'follow':follow, 'user_follow':user_follow})

@login_required
def friends_list(request):
    follow = Follower.objects.get(profile=request.user.profile)
    profiles = follow.get_friends()
    
    return render(request, 'friends.html', {'profiles':profiles})

@login_required
def view_post(request, post_id):
    postGet = Post.objects.get(id=post_id)
    likedUser = request.user.profile
    likePosts = Like.objects.filter(post=postGet)
    likes = len(likePosts)

    comments = Comment.objects.filter(post=postGet).order_by("-published")
    commentCount = len(comments)

    liked = True
    data = Like.objects.filter(post=postGet, author=likedUser)
    if len(data) > 0:
        liked = True
    else:
        liked = False

    if request.method == "POST":
        action = request.POST['action']
        if action == "like":
            like = Like(summary="",author=likedUser, post=postGet, object="")
            like.save()
            messages.success(request, ("Post Liked successfully!"))
        elif action == "unlike":
            like = Like.objects.filter(post=postGet, author=likedUser).delete()
            messages.success(request, ("Post unliked successfully!"))
        return redirect("home")
    return render(request, "view_post.html", {"post":postGet, "likes":likes, "liked":liked, "comments":comments, "commentCount":commentCount})
    
class PostDetail(APIView):
    def get(self, request, *args, **kwargs):
        """
        Get the public post whose id is POST_ID
        """
        try:
            post = Post.objects.get(id=kwargs['post_id'])
            serializer = PostSerializer(post)
            return Response(serializer.data, status=201)
        except Post.DoesNotExist:
            return Response(status=404)
        
    @swagger_auto_schema( request_body=PostSerializer)
    def post(self, request, *args, **kwargs):
        """
        Update the post whose id is POST_ID (must be authenticated)
        TODO: Do Authentication Check
        """
        try:
            post = Post.objects.get(id=kwargs['post_id'])
        except Post.DoesNotExist:
            return Response(status=404)
        request_data = json.loads(request.body.decode("utf-8"))
        request_data['author'] = kwargs['author_id']
        serializer = PostSerializer(post, data=request_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
        
        
    def delete(self, request, *args, **kwargs):
        """
        Remove the post whose id is POST_ID
        """
        try:
            post = Post.objects.get(id=kwargs['post_id'])
            post.delete()
            return Response("Post Deleted", status=200)
        except Post.DoesNotExist:
            return Response("Post not found", status=404)
        
    @swagger_auto_schema( request_body=PostSerializer)
    def put(self, request, *args, **kwargs):
        """
        Create a post where its id is POST_ID
        """
        try:
            request_data = json.loads(request.body.decode("utf-8"))
            new_instance = Post()
            new_instance.id = kwargs['post_id']
            request_data['author'] = kwargs['author_id']
            serializer = PostSerializer(new_instance, data=request_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        except IntegrityError as e:
            return Response({"error": f"Post with id '{new_instance.id}' already exists"}, status=400)
    
class PostList(APIView):
    def get(self, request, *args, **kwargs):
        """
        Get the recent posts from author AUTHOR_ID (paginated)
        TODO: Add pagination
        """
        size = request.GET.get('size')
        page = request.GET.get('page')
        if size == '0':
            return Response({'error': "Invalid Query Parameter: Size = 0"}, status=400)
        elif page is not None and not page.isdigit():
            return Response({'error': f"Invalid Query Parameter: Page '{page}'"}, status=400)
        elif size is not None and not size.isdigit():
            return Response({'error': f"Invalid Query Parameter: Size '{size}'"}, status=400)

        if not size:
            size = 25
        posts = Post.objects.filter(models.Q(author__id=kwargs['author_id'])).order_by('-published')
        paginator = Paginator(posts, per_page=size)
        page_object = paginator.get_page(page)
        serializer = PostSerializer(page_object, many=True)
        return Response(serializer.data, status=200)
        
    @swagger_auto_schema( request_body=PostSerializer)
    def post(self, request, *args, **kwargs):
        """
        Create a new post but generate a new id
        """
        request_data = json.loads(request.body.decode("utf-8"))
        request_data['author'] = kwargs['author_id']
        serializer = PostSerializer(data=request_data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class Followers(APIView):
    def get(self, request, *args, **kwargs):
        """
        Returns list of authors who are AUTHOR_ID's followers
        """
        try: 
            author_id = kwargs['author_id']
            follow = Follower.objects.get(profile__id=author_id)
            followers = follow.get_followers()
            serializer = ProfileSerializer(followers, many=True)
            return Response(serializer.data, status=200)
        except Follower.DoesNotExist:
            return Response({'error': 'Author does not exist'}, status=404)


class FollowersAction(APIView):
    def get(self, request, *args, **kwargs):
        """
        Returns if FOREIGN_AUTHOR_ID is a follower of AUTHOR_ID
        """
        try:
            author_id = kwargs['author_id']
            foreign_author_id = kwargs['foreign_author_id']
            follow = Follower.objects.get(profile__id=author_id)
            followers = follow.get_followers()
            foreign_profile = Profile.objects.get(id=foreign_author_id)
            is_follower = foreign_profile in followers
            response_data = {'is_follower': is_follower}
            return Response(response_data, status=200)
        except Follower.DoesNotExist:
            return Response({'error': 'Author does not exist'}, status=404)
        except Profile.DoesNotExist:
            return Response({'error': 'Foreign Author does not exist'}, status=404)

    def put(self, request, *args, **kwargs):
        """
        Add FOREIGN_AUTHOR_ID as a follower of AUTHOR_ID
        TODO: Must be authenticated
        """
        try:
            author_id = kwargs['author_id']
            foreign_author_id = kwargs['foreign_author_id']
            follow = Follower.objects.get(profile__id=foreign_author_id)
            foreign_following = follow.following
            author_profile = Profile.objects.get(id=author_id)
            
            if author_profile not in foreign_following.all():
                follow.following.add(author_profile)
                return Response({'message': 'Now following.'}, status=200)
            else:
                return Response({'message': 'Already following.'}, status=200)
        except Follower.DoesNotExist:
            return Response({'error': 'Author does not exist'}, status=404)
        except Profile.DoesNotExist:
            return Response({'error': 'Foreign Author does not exist'}, status=404)


    def delete(self, request, *args, **kwargs):
        """
        Remove FOREIGN_AUTHOR_ID as a follower of AUTHOR_ID
        """
        try:
            author_id = kwargs['author_id']
            foreign_author_id = kwargs['foreign_author_id']
            follow = Follower.objects.get(profile__id=foreign_author_id)
            foreign_following = follow.following
            author_profile = Profile.objects.get(id=author_id)

            if author_profile in foreign_following.all():
                foreign_following.remove(author_profile)
                return Response({'message': 'Now unfollowed'}, status=200)
            else:
                return Response({'message': 'Cannot unfollow, not following.'}, status=200)
        except Follower.DoesNotExist:
            return Response({'error': 'Author does not exist'}, status=404)
        except Profile.DoesNotExist:
            return Response({'error': 'Foreign Author does not exist'}, status=404)
    
class Likes(APIView):
    def get(self, request, *args, **kwargs):
        """
        Returns notifications of likes for AUTHOR_ID
        """
        author_id = kwargs['author_id']
        author_likes = Likes.objects.filter(profile_id=author_id)
        serializer = LikeSerializer(author_likes, many=True)
        return Response(serializer.data, status=200)
