import json
from django.db import IntegrityError, models
from rest_framework.views import APIView
from author.models import Follower, Profile, FriendFollowRequest
from post.models import Post, Like, Comment
from inbox.models import Inbox
from .serializers import ProfileSerializer, PostSerializer, LikeSerializer, CommentSerializer
from rest_framework.response import Response
from django.core.paginator import Paginator
from drf_yasg.utils import swagger_auto_schema

# Create your views here.
class Authors(APIView):
    def get(self, request, *args, **kwargs):
        """
        Returns list of profiles on the server 
        TODO: Add pagination
        """
        authors = Profile.objects.all()
        serializer = ProfileSerializer(authors, many=True, context={'request':request})
        response_data = {'type': 'authors', 'items': serializer.data}
        return Response(response_data, status=200)

class Author(APIView):
    def get(self, request, *args, **kwargs):
        """
        Returns AUTHOR_ID's profile
        """
        try: 
            author_id = kwargs['author_id']
            author = Profile.objects.get(id=author_id)
            serializer = ProfileSerializer(author, context={'request':request})
            response_data = serializer.data
            return Response(response_data, status=200)
        except Profile.DoesNotExist:
            return Response({'error': 'Author does not exist'})
    
class PostDetail(APIView):
    def get(self, request, *args, **kwargs):
        """
        Get the public post whose id is POST_ID
        """
        try:
            post = Post.objects.get(id=kwargs['post_id'])
            serializer = PostSerializer(post, context={'request': request})
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
        serializer = PostSerializer(page_object, many=True, context={'request': request})
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
            serializer = ProfileSerializer(followers, many=True, context={'request':request})
            response_data = {'type': 'followers', 'items': serializer.data}
            return Response(response_data, status=200)
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

class Comments(APIView):
    def get(self, request, *args, **kwargs):
        """
        Returns the list of comments of the post whose id is POST_ID (paginated)
        TODO: pagination
        """
        author_id = kwargs['author_id']
        post_id = kwargs['post_id']
        post = Post.objects.get(id=post_id)
        comments = Comment.objects.filter(post_id=post_id)
        comment_serializer = CommentSerializer(comments, many=True, context={'request': request})
        post_serializer = PostSerializer(post, context={'request': request})
        post_link = post_serializer.data['id']
        return Response({'type': 'comments', 'id': request.build_absolute_uri(), 
                         'post': post_link, 'comments': comment_serializer.data}, status=200)
    
class Likes(APIView):
    def get(self, request, *args, **kwargs):
        """
        Returns notifications of likes for AUTHOR_ID
        """
        author_id = kwargs['author_id']
        author_likes = Likes.objects.filter(profile_id=author_id)
        serializer = LikeSerializer(author_likes, many=True)
        return Response(serializer.data, status=200)
