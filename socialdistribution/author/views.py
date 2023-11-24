from api.models import Node
from . import services
from .models import Profile, Follower, FriendFollowRequest, SiteConfiguration
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

# Create your views here.
class CustomLoginView(LoginView):
    form_class = LoginUser

    def form_valid(self, form):
        config = SiteConfiguration.objects.all()[:1].get()
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
            node_authors = node_authors_data['items']
            for index, remote_author in enumerate(node_authors):
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
        inbox = Inbox.objects.get(user=user_profile)
        user_follow = Follower.objects.get(profile=user_profile)
        other_inbox = Inbox.objects.get(user=profile)    

        # Post form logic
        if request.method == "POST":
            action = request.POST['follow']
            if action == "unfollow":
                user_follow.following.remove(profile)
                inbox.follows.remove(profile)
                friend_request = FriendFollowRequest.objects.filter(follower=user_profile, followee=profile).delete()
            elif action == "follow":
                user_follow.following.add(profile)
                inbox.follows.add(profile)
                req_summary = request.user.username + " has requested to follow you!"
                friend_request = FriendFollowRequest(summary=req_summary, follower=user_profile, followee=profile)
                friend_request.save()
                other_inbox.requests.add(friend_request)
            user_follow.save()

        return render(request, 'other_profiles.html', {'profile':profile, 'follow':follow, 'user_follow':user_follow})
        
@login_required
def friends_list(request):
    follow = Follower.objects.get(profile=request.user.profile)
    profiles = follow.get_friends()
    
    return render(request, 'friends.html', {'profiles':profiles})

@login_required
def send_remote_follow(request, remote_author, node):
    author_node = Node.objects.get(name=node)
    services.put_follower_into_node(author_node, request.user.profile.id, remote_author)
    return redirect('social')
        
@login_required
def send_remote_unfollow(request, remote_author, node):
    author_node = Node.objects.get(name=node)
    services.delete_follower_from_node(author_node, request.user.profile.id, remote_author)
    return redirect('social')
