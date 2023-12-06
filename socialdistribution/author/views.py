from api.models import Node
from api.serializers import ProfileSerializer
from api.utils import get_base_url
from . import services
from .models import FollowerRemote, Profile, Follower, FriendFollowRequest, RemoteFriendFollowRequest, SiteConfiguration
from inbox.models import Inbox
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from .forms import RegisterUser, LoginUser, UpdateUserForm, UpdateProfileForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import User

# Create your views here.
class CustomLoginView(LoginView):
    form_class = LoginUser

    def form_valid(self, form):
        config, created = SiteConfiguration.objects.get_or_create(pk=1)
        user_approval_required = config.user_approval_required
        if user_approval_required:
            if not self.request.user.is_authenticated:
                user_profile = Profile.objects.get(user=form.user_cache)
                if not user_profile.approved:
                    messages.success(self.request, 'Admin approval required')
                    return redirect(to='/')
            
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
            user = User.objects.get(username=username)
            profile = Profile.objects.get(user=user)
            profile.github = form.cleaned_data.get('github')
            profile.save()
            
            messages.success(request, f'Account created for {username}')

            return redirect(to='/')

        return render(request, self.template_name, {'form': form})

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
    
class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('home')    

@login_required
def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user)
        nodes = Node.objects.all()
        nodes_map = {}
        
        for node in nodes:
            node_authors_data = services.get_authors_from_node(node)
            if node_authors_data == {}:
                continue

            if node.name == 'A-Team':
                node_authors = node_authors_data['results']['items']
            else:
                node_authors = node_authors_data['items']

            for index, remote_author in enumerate(node_authors):
                if node.name == 'A-Team':
                    # changing fields
                    remote_author['id'] = remote_author['url']
                    remote_author['profileImage'] = remote_author['profilePicture']
                following_data = services.get_following_from_node(node, request.user.profile.id, remote_author['id'])
                remote_author.update(following_data)
                node_authors[index] = remote_author
            nodes_map[node] = node_authors
        user_profile = request.user.profile
        user_follow = Follower.objects.get(profile=user_profile)   
                
        return render(request, 'social.html', {"profiles":profiles, "nodes":nodes_map, "user_follow":user_follow})

@login_required
def profile_detail(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        follow = Follower.objects.get(profile=profile)
        user_profile = request.user.profile
        user_follow = Follower.objects.get(profile=user_profile)
        other_inbox = Inbox.objects.get(user=profile)
        pending = False

        # Post form logic
        if request.method == "POST":
            action = request.POST['follow']
            if action == "unfollow":
                print("NOT IMPLEMENTED. FRIENDS FOREVER :D")
            elif action == "follow":
                # Check if a follow request already exists
                existing_request = FriendFollowRequest.objects.filter(follower=request.user.profile, followee=profile, status='pending').first()

                if not existing_request:
                    req_summary = request.user.username + " has requested to follow you!"
                    friend_request = FriendFollowRequest(summary=req_summary, follower=user_profile, followee=profile)
                    friend_request.save()
                    other_inbox.requests.add(friend_request)
                    pending = True

        return render(request, 'other_profiles.html', {'profile':profile, 'follow':follow, 'user_follow':user_follow, 'pending':pending})
        
@login_required
def friends_list(request):
    follow = Follower.objects.get(profile=request.user.profile)
    profiles = follow.get_friends()
    follow_remote = FollowerRemote.objects.filter(following_author=request.user.profile)

    remote_profiles = []
    for follow_obj in follow_remote:
        base_url = get_base_url(follow_obj.url)
        node = Node.objects.get(url=base_url)
        is_remote_following = services.get_following_from_node(node, request.user.profile.id, follow_obj.url)
        if is_remote_following['is_follower']:
            remote_author = services.get_author_from_node(node, follow_obj.url)
            remote_profiles.append(remote_author)

    return render(request, 'friends.html', {'profiles':profiles, 'remote_profiles': remote_profiles})

@login_required
def send_remote_follow(request, remote_author, node):
    author_node = Node.objects.get(name=node)
    user_profile = request.user.profile
    serializer = ProfileSerializer(user_profile, context={'request':request})
    remote_author_data = services.get_author_from_node(author_node, remote_author)
    if node == 'A-Team':
        data = {
            'actor': serializer.data['id'].split('/')[-1],
            'ojbect': remote_author,
        }
    else:
        data = {
            'type': 'follow',
            'summary': f'{user_profile} wants to follow {remote_author_data["displayName"]}',
            'actor': serializer.data,
            'object': remote_author_data
        }
    services.post_following_to_node(author_node, remote_author, data)
    
    return redirect('social')
        
@login_required
def send_remote_unfollow(request, remote_author, node):
    print("NOT IMPLEMENTED. FRIENDS FOREVER :D")
    return redirect('social')

@login_required
def respond_to_follow_request(request, friend_request_id, action):
    friend_request = FriendFollowRequest.objects.get(pk=friend_request_id)
    
    if friend_request.followee == request.user.profile:
        if action == 'accept':
            user_followee = Follower.objects.get(profile=friend_request.follower)
            user_followee.following.add(request.user.profile)
            friend_request.status = 'accepted'
            friend_request.save()
            FriendFollowRequest.objects.filter(follower=friend_request.follower, followee=request.user.profile).delete()
        elif action == 'decline':
            friend_request.status = 'declined'
            friend_request.save()
            FriendFollowRequest.objects.filter(follower=friend_request.follower, followee=request.user.profile).delete()
    
    return redirect('social')

@login_required
def respond_to_remote_follow_request(request, remote_friend_request_id, action):
    remote_friend_request = RemoteFriendFollowRequest.objects.get(pk=remote_friend_request_id)
    
    if remote_friend_request.followee == request.user.profile:
        if action == 'accept':
            remote_id = remote_friend_request.follower.split('/')[-1]
            FollowerRemote.objects.create(
                following_author=request.user.profile, 
                remote_id=remote_id,
                url=remote_friend_request.follower)
            remote_friend_request.status = 'accepted'
            remote_friend_request.save()
        elif action == 'decline':
            remote_friend_request.status = 'declined'
            remote_friend_request.save()
    
    return redirect('inbox')
