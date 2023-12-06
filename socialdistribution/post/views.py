import json, requests
from api.utils import get_base_url
from . import services
from api.models import Node
from api.services import get_remote_node
from .utils import parse_iso8601_time  
from . import services as postservices
from author import services as authorservices
from .models import Post, Like, Comment, CommentLike, RemoteLike, RemoteComment, RemotePost
from author.models import Follower, Profile, FollowerRemote
from inbox.models import Inbox, RemoteInbox
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CreatePostForm, CreateCommentForm, CreateRemoteCommentForm
from datetime import datetime
from django.utils import timezone

# Create your views here.
@login_required
def home_page(request):
    if request.user.is_authenticated:

        # retrieve remote posts
        nodes = Node.objects.all()
        nodes_map = {}
        node_images = {}
        for node in nodes:
            node_authors_data = authorservices.get_authors_from_node(node)
            if node_authors_data == {}:
                continue
            if node.name == 'A-Team':
                node_authors = node_authors_data['results']['items']
            else:
                node_authors = node_authors_data['items']
            node_posts = []
            for index, remote_author in enumerate(node_authors):
                if node.name == 'A-Team':
                    remote_author['id'] = remote_author['url']
                node_post_data = postservices.get_posts_from_node(node, remote_author['id'])
                if isinstance(node_post_data, dict) and node_post_data != {}:
                    if node.name == 'A-Team':
                        node_post_data = node_post_data['results']['items']
                    else:
                        node_post_data = node_post_data['items']
                for post in node_post_data:
                    if post['visibility'].lower() == 'public':
                        # get image
                        if node.name == 'A-Team' and post['image'] != "":
                            node_images[post['id']] = post['image']
                        elif node.name != 'A-Team':
                            node_image_data = postservices.get_image_from_node(node, post['id']) 
                            if node_image_data == {}:
                                continue
                            elif type(node_image_data) == dict and node_image_data['image'] != "":  # our format
                                node_images[post['id']] = node_image_data['image']
                            elif type(node_image_data) == str and node_image_data != "":  # packet pirate format
                                node_images[post['id']] = node_image_data

                        post['published'] = parse_iso8601_time(post['published'])
                            
                        node_posts.append(post)
            node_posts.reverse()
            nodes_map[node] = node_posts

        # retrieve local posts
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

                    # send posts to remote followers and friends
                    if post.visibility == "public": 
                        follow_remote = FollowerRemote.objects.filter(following_author=request.user.profile)
                        for follow_obj in follow_remote:
                            node = get_remote_node(follow_obj.url)
                            if node.name == 'A-Team':
                                # TODO
                                print('IS A-TEAM')
                                continue
                            postservices.send_local_post_to_node(post, follow_obj.url, request) 
                            print('SENT POST')
                    elif post.visibility == "friends": 
                        follow_remote = FollowerRemote.objects.filter(following_author=request.user.profile)
                        for follow_obj in follow_remote:
                            base_url = get_base_url(follow_obj.url)
                            node = Node.objects.get(url=base_url)
                            is_remote_following = authorservices.get_following_from_node(node, request.user.profile.id, follow_obj.url)
                            if is_remote_following['is_follower']:
                                if node.name == 'A-Team':
                                    # TODO
                                    continue
                                postservices.send_local_post_to_node(post, follow_obj.url, request) 

                    return redirect('home')
            elif action == "load_github":
                #print('loading github...')
                details = load_github(request.user.profile)
                if details != None:
                    new_post = Post(title="Github Activities", description=details, author=request.user.profile, visibility="friends")
                    new_post.save()
                    messages.success(request, "Github activities post created sucessfully!")
                else:
                    messages.warning(request, "Invalid github profile!")
            return redirect("home")

        else:
            form = CreatePostForm()
        return render(request, 'home.html', {"posts":posts, "form":form, "nodes":nodes_map, "images":node_images})


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

    # get remote friends
    follow_remote = FollowerRemote.objects.filter(following_author=request.user.profile)
    friends_remote = []
    for follow_obj in follow_remote:
        base_url = get_base_url(follow_obj.url)
        node = Node.objects.get(url=base_url)
        is_remote_following = authorservices.get_following_from_node(node, request.user.profile.id, follow_obj.url)
        if is_remote_following['is_follower']:
            remote_author = authorservices.get_author_from_node(node, follow_obj.url)
            friends_remote.append(remote_author)

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

        # check if the profile is friend with the person who commented on the post
        post = comment.post
        # print(post.visibility)
        if post.visibility == "friends":
            commentAuthor = comment.author
            postAuthor = postGet.author
            # this author is the author of the comment
            isCommentAuthor = request.user.profile == commentAuthor
            # this author is the author of the post
            isPostAuthor = request.user.profile == postAuthor
            # the comment is created by the post author
            isAuthor = commentAuthor == postAuthor

            if (isCommentAuthor or isPostAuthor or isAuthor):
                commentsInfo.append([comment, commentLikes, isLiked, index])    
                index += 1   

        else:
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
            commentIndex = commentAction[1]
            if commentLiking == "like":
                likeSummary = likedUser.user.username + " liked your comment!"
                like = CommentLike(summary=likeSummary, author=likedUser,comment=commentsInfo[commentIndex][0])
                like.save()
                #inbox.comment_likes.add(like)
                if commentsInfo[int(commentIndex)][0].author.user.profile != likedUser:
                    other_inbox = Inbox.objects.get(user=commentsInfo[int(commentIndex)][0].author.user.profile)
                    other_inbox.comment_likes.add(like)
                    other_inbox.save()
                messages.success(request, ("Comment Liked successfully!"))
            elif commentLiking == "unlike":
                like = CommentLike.objects.filter(author=likedUser,comment=commentsInfo[int(commentIndex)][0]).delete()
                messages.success(request, ("Comment Unliked successfully!"))
            elif commentLiking == "share":
                friend_id = commentIndex
                postservices.send_local_post_to_node(postGet, friend_id, request)
                messages.success(request, "Shared Post sucessfully!")

        inbox.save()
        return redirect("home")
    return render(request, "view_post.html", 
                  {"post":postGet, 
                   "likes":likes, 
                   "liked":liked, 
                   "commentsInfo":commentsInfo, 
                   "commentCount":commentCount, 
                   "form": form, 
                   "friends":friends, 
                   "friends_remote":friends_remote})

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

@login_required
def share_remote_post(request, node, remote_post, friend_id):
    profile = Profile.objects.get(user_id=friend_id)
    remote_inbox = RemoteInbox.objects.get(author=profile)
    new_remote_post = RemotePost.objects.filter(post_id=remote_post)
    if (len(new_remote_post) == 0):
        new_remote_post = RemotePost(post_id=remote_post)
        new_remote_post.save()
    else:
        new_remote_post = RemotePost.objects.get(post_id=remote_post)
    if request.method == "POST":
        action = request.POST['confirm']
        if action == 'yes':
            remote_inbox.posts.add(new_remote_post)
            remote_inbox.save()
            return redirect("view_remote_post", node, remote_post)
    return render(request, "share_remote_post.html", {'post':new_remote_post, 'shared_posts':list(remote_inbox.posts.all()), 'node_name':node})


@login_required
def view_remote_post(request, node, remote_post):

    likes = 0
    comment_count = 0
    node_name = node
    # get local freinds
    follow_local = Follower.objects.get(profile=request.user.profile)
    friends_local = follow_local.get_friends()

    # get remote friends
    follow_remote = FollowerRemote.objects.filter(following_author=request.user.profile)
    friends_remote = []
    for follow_obj in follow_remote:
        base_url = get_base_url(follow_obj.url)
        node = Node.objects.get(url=base_url)
        is_remote_following = authorservices.get_following_from_node(node, request.user.profile.id, follow_obj.url)
        if is_remote_following['is_follower']:
            remote_author = authorservices.get_author_from_node(node, follow_obj.url)
            friends_remote.append(remote_author)
    # get the remote post
    cur_node = Node.objects.get(name=node_name)
    post_details = ""
    node_image = ""
    
    if cur_node.name == 'A-Team':
        remote_post = remote_post + '/'
    post = postservices.get_post_from_node(cur_node, remote_post)
    if cur_node.name == 'A-Team':
        post = post[0]

    if cur_node.name == 'A-Team' and post['image'] != "":
        node_image = post['image']
    elif cur_node.name != 'A-Team':
        node_image_data = postservices.get_image_from_node(cur_node, remote_post)
        if type(node_image_data) == dict and node_image_data['image'] != "":  # our format
            node_image = node_image_data['image']
        elif type(node_image_data) == str and node_image_data != "":  # packet pirate format
            node_image = node_image_data
        post['published'] = parse_iso8601_time(post['published'])
    
    # get remote comments and likes
    comments = []
    comment_list = []
    
    node_comments_data = postservices.get_comments_from_node(cur_node, post['id'])
    print(node_comments_data)

    if type(node_comments_data) == dict and node_comments_data != {}:
        if cur_node.name == 'A-Team':
            comment_list = node_comments_data['results']['comments']
        else:
            comment_list = node_comments_data['comments']
    elif type(node_comments_data) == list:
            comment_list = node_comments_data
            
    for comment in comment_list:
        comment['published'] = parse_iso8601_time(comment['published'])
        comments.append(comment)
        comment_count += 1

    node_likes_data = postservices.get_likes_from_node(cur_node, post['id'])
    likes += len(node_likes_data)

    # create local comments and likes
    form = CreateRemoteCommentForm(request.POST or None)
    if request.method == "POST":
        action = request.POST['action']
        if action == "like":
            # send like to their inbox
            postservices.send_like_to_node(cur_node, remote_post, request)    
            messages.success(request, ("Post Liked successfully!"))
        elif action == "unlike": 
            messages.success(request, ("Post unliked successfully!"))
        elif action == "comment":
            # send comment to their inbox
            if form.is_valid():
                form.instance.published = timezone.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                comment = form.save(commit=False)
                postservices.send_comment_to_node(cur_node, comment, remote_post, request)
                messages.success(request, ("Commented on post successfully!"))
        elif "share" in action:
            friend_id = action.split(",")[1]
            postservices.send_remote_post_to_node(cur_node, remote_post, friend_id, request)
            messages.success(request, "Shared Post sucessfully!")
        return redirect("home")
    return render(request, "view_remote_post.html", {'post_details':post, 'image':node_image, 'comments':comments, 'form': form, 'likes':likes, 'comment_count':comment_count, "friends_local":friends_local, "friends_remote":friends_remote, "node_name":node_name})

def load_github(user : Profile):
    """
    retrieve github activities for the author
    """

    username = user.github
    if (not username):
        return None
    username = username.split("/")[3]

    # GitHub API endpoint for user's public activity feed    
    url = f'https://api.github.com/users/{username}/events/public'

    # Make a GET request to the API    
    response = requests.get(url)

    # Check if the request was successful    
    if response.status_code == 200:    
    # Parse the JSON response    
        activity = response.json()    

        details = ""
        # Print the user's public activity    
        for event in activity:    
            #print(json.dumps(event, indent=2))   
            # print(event)
            detail = f"{event['actor']['login']} PEFORMED {event['type']} ON REPO {event['repo']['name']} DURING {event['created_at']};\n"
            
            details += detail
        return details
    else:    
        return None