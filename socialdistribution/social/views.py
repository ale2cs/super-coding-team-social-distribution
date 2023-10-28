import json
from django.db import models
from rest_framework.views import APIView
from .models import Profile, Post, Follower, FriendFollowRequest
from .serializers import ProfileSerializer, PostSerializer, FollowerSerializer
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


def home_page(request):
    if request.user.is_authenticated:
        posts = Post.objects.all().order_by("-published")
        form = CreatePostForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user.profile
                post.save()
                messages.success(request, ("Post created successfully!"))
                return redirect('home')
        return render(request, 'home.html', {"posts":posts, "form":form})

    posts = Post.objects.all().order_by("-published")
    return render(request, 'home.html', {"posts":posts})

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
        print('HERE')

        # Post form logic
        if request.method == "POST":
            print('yerrr')
            action = request.POST['follow']
            if action == "unfollow":
                user_follow.following.remove(profile)
            elif action == "follow":
                user_follow.following.add(profile)
            user_follow.save()

        return render(request, 'other_profiles.html', {'profile':profile, 'follow':follow, 'user_follow':user_follow})

    
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
        request_data = json.loads(request.body.decode("utf-8"))
        new_instance = Post()
        new_instance.id = kwargs['post_id']
        request_data['author'] = kwargs['author_id']
        serializer = PostSerializer(new_instance, data=request_data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
class PostList(APIView):
    def get(self, request, *args, **kwargs):
        """
        Get the recent posts from author AUTHOR_ID (paginated)
        TODO: Add pagination
        """
        size = request.GET.get('size')
        if not size:
            size = 25
        elif size == '0':
            return Response("Invalid Query Parameter: Size = 0", status=400)
        page = request.GET.get('page')
        posts = Post.objects.filter(models.Q(author__id=kwargs['author_id'])).order_by('-published')
        paginator = Paginator(posts, per_page=size)
        page_object = paginator.get_page(page)
        serializer = PostSerializer(page_object, many=True)
        return Response(serializer.data, status=201)
        
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
        Returns list of followers from author AUTHOR_ID
        """
        author_id = kwargs['author_id']
        author_followers = Followers.objects.filter(profile__id=author_id)
        serializer = FollowerSerializer(author_followers, many=True)
        return Response(serializer.data, status=201)