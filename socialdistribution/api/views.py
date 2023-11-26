import json
from django.db import IntegrityError
from django.db.models import Q
from rest_framework.views import APIView
from author.models import Follower, FollowerRemote, Profile, FriendFollowRequest
from post.models import Post, Like, Comment, CommentLike
from inbox.models import Inbox
from .serializers import ProfileSerializer, PostSerializer, LikeSerializer, CommentSerializer, FollowSerializer, InboxSerializer, CommentLikeSerializer
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils import get_field_type, validate_paginator_parameters

DEFAULT_PAGE_SIZE = 25

# Create your views here.
class Authors(APIView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: ProfileSerializer,
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Error: Unauthorized",
                examples={
                    'text/plain': 'Unauthorized.',
                },
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        """
        Returns list of profiles on the server 
        """
        size = request.GET.get('size')
        page = request.GET.get('page')

        error_response, error_status = validate_paginator_parameters(size, page)
        if error_response is not None:
            return Response(error_response, status=error_status)

        if not size:
            size = DEFAULT_PAGE_SIZE

        authors = Profile.objects.all()
        paginator = Paginator(authors, per_page=size)
        page_object = paginator.get_page(page)
        serializer = ProfileSerializer(page_object, many=True, context={'request':request})
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
            return Response(response_data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({'error': 'Author does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
class PostDetail(APIView):
    @swagger_auto_schema(responses={201: PostSerializer})
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
        
    '''
    @swagger_auto_schema(request_body=PostSerializer)
    def post(self, request, *args, **kwargs):
        """
        Update the post whose id is POST_ID (must be authenticated)
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
    '''
    
class PostList(APIView):
    @swagger_auto_schema(responses={200: PostSerializer(many=True)})
    def get(self, request, *args, **kwargs):
        """
        Get the recent posts from author AUTHOR_ID (paginated)
        """
        size = request.GET.get('size')
        page = request.GET.get('page')

        error_response, error_status = validate_paginator_parameters(size, page)
        if error_response is not None:
            return Response(error_response, status=error_status)

        if not size:
            size = DEFAULT_PAGE_SIZE
        posts = Post.objects.filter(Q(author__id=kwargs['author_id'])).order_by('-published')
        paginator = Paginator(posts, per_page=size)
        page_object = paginator.get_page(page)
        serializer = PostSerializer(page_object, many=True, context={'request': request})
        return Response(serializer.data, status=200)
        
    '''
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
    '''

class Followers(APIView):
    @swagger_auto_schema(responses={200: ProfileSerializer(many=True)})
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


'''
class FollowersAction(APIView):
    @swagger_auto_schema(responses={200: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'is_follower': openapi.Schema(type=openapi.TYPE_BOOLEAN)}
    )})
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

    @swagger_auto_schema(responses={200: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'message': openapi.Schema(type=openapi.TYPE_STRING)}
    )})
    def put(self, request, *args, **kwargs):
        """
        Add FOREIGN_AUTHOR_ID as a follower of AUTHOR_ID
        """
        try:
            author_id = kwargs['author_id']
            foreign_author_id = kwargs['foreign_author_id']
            follow = Follower.objects.get(profile__id=author_id)
            # if not follow.exists():
            #     follow_remote = FollowerRemote.objects.filter()
            #     if not follow_remote.exists():
            #         FollowerRemote.objects.create(id=foreign_author_id)
            # foreign_following = follow.followingRemote
            # author_profile = Profile.objects.get(id=author_id)
            
            if foreign_author_id not in follow.followingRemote.all():
                follow.followingRemote.add(foreign_author_id)
                return Response({'message': 'Now following.'}, status=200)
            else:
                return Response({'message': 'Already following.'}, status=200)
        except Profile.DoesNotExist:
            return Response({'error': 'Author does not exist'}, status=404)
        except Follower.DoesNotExist:
            FollowerRemote.objects.create(id=foreign_author_id)
            return Response({'error': 'Foreign Author does not exist'}, status=404)
            Profile.objects.create(id=foreign_author_id)
            follow = Follower.objects.get(profile__id=foreign_author_id)
            author_profile = Profile.objects.get(id=author_id)
            follow.following.add(author_profile)
            return Response({'message': 'Now following.'}, status=200)


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
'''

class Comments(APIView):
    @swagger_auto_schema(responses={200: CommentSerializer(many=True)})
    def get(self, request, *args, **kwargs):
        """
        Returns the list of comments of the post whose id is POST_ID (paginated)
        """
        size = request.GET.get('size')
        page = request.GET.get('page')

        error_response, error_status = validate_paginator_parameters(size, page)
        if error_response is not None:
            return Response(error_response, status=error_status)

        if not size:
            size = DEFAULT_PAGE_SIZE

        post_id = kwargs['post_id']
        post = Post.objects.get(id=post_id)
        comments = Comment.objects.filter(post_id=post_id)
        paginator = Paginator(comments, per_page=size)
        page_object = paginator.get_page(page)
        comment_serializer = CommentSerializer(page_object, many=True, context={'request': request})
        post_serializer = PostSerializer(post, context={'request': request})
        post_link = post_serializer.data['id']
        return Response({'type': 'comments', 'page': page, 'size': size, 
                         'id': request.build_absolute_uri(), 
                         'post': post_link, 'comments': comment_serializer.data}
                         , status=200)

class LikesOnPost(APIView):
    @swagger_auto_schema(responses={200: CommentSerializer(many=True)})
    def get(self, request, *args, **kwargs):
        """
        Returns list of likes from other authors on AUTHOR_ID's post POST_ID
        """
        post_id = kwargs['post_id']
        likes = Like.objects.filter(post_id=post_id)
        serializer = LikeSerializer(likes, many=True, context={'request': request})
        return Response(serializer.data, status=200)

class LikesOnComment(APIView):
    def get(self, request, *args, **kwargs):
        """
        Returns list of likes from other authors on AUTHOR_ID's post POST_ID
        comment COMMENT_ID
        """
        comment_id = kwargs['comment_id']
        likes = CommentLike.objects.filter(comment_id=comment_id)
        serializer = CommentLikeSerializer(likes, many=True, context={'request': request})
        return Response(serializer.data, status=200)

class LikedPosts(APIView):
    @swagger_auto_schema(responses={200: LikeSerializer(many=True)})
    def get(self, request, *args, **kwargs):
        """
        Returns list of what public things AUTHOR_ID liked
        """
        author_id = kwargs['author_id']
        public_post_query = Q(post__visibility='public') & Q(post__unlisted=False)
        author_likes = Like.objects.filter(Q(author_id=author_id) & public_post_query)
        serializer = LikeSerializer(author_likes, many=True, context={'request': request})
        return Response({'type': 'liked', 'items':serializer.data}, status=200)

class InboxAdd(APIView):
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'type': openapi.Schema(type=openapi.TYPE_STRING),
            'author': openapi.Schema(type=openapi.TYPE_STRING),
            'items': openapi.Schema(
                description='Items can be of type: Post, Follow, Like, Comment. See models section.\nCurrent Example is of Post.',
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        field_name: openapi.Schema(type=get_field_type(field)) for field_name, field in PostSerializer().fields.items()
                    },
                )
            )
        }
    ))
    def post(self, request, *args, **kwargs):
        """
        Adds a post, follow, like, or comment object to AUTHOR_ID's inbox
        """
        author_id = kwargs['author_id']
        try:
            inbox = Inbox.objects.get(user_id=author_id)
        except Inbox.DoesNotExist:
            return Response({'message': 'AUTHOR_ID does not exist'},status=404)
        new_object = False
        request_data = json.loads(request.body.decode("utf-8"))
        type_value = request_data['type']
        if type_value == 'post':
            post_id = request_data['id'].split('/')[-1]
            try:
                post = Post.objects.get(id=post_id)
                serializer = PostSerializer(post, context={'request': request})
            except Post.DoesNotExist:
                request_data['id'] = post_id
                serializer = PostSerializer(data=request_data, context={'request': request})
                post = Post.objects.get(id=post_id)
                new_object = True 
            if post not in inbox.posts.all():
                inbox.posts.add(post)
        elif type_value == 'follow':
            # TODO not working
            actor_id = request_data['actor']
            object_id = request_data['object']
            try:
                friend_request = FriendFollowRequest.objects.get(follower_id=actor_id, followee_id=object_id)
                serializer = FollowSerializer(friend_request, context={'request': request})
            except FriendFollowRequest.DoesNotExist:
                serializer = FollowSerializer(data=request_data, context={'request': request})
                friend_request = FriendFollowRequest.objects.get(follower_id=actor_id, followee_id=object_id)
                new_object = True
            if friend_request not in inbox.requests.all():
                inbox.requests.add(friend_request)
        elif type_value == 'commment':
            comment_id = request_data['id'].split('/')[-1]
            try:
                comment = Comment.objects.get(id=comment_id)
                serializer = CommentSerializer(comment, context={'request': request})
            except Comment.DoesNotExist:
                request_data['id'] = comment_id
                serializer = CommentSerializer(data=request_data, context={'request': request})
                post = Comment.objects.get(id=comment_id)
                new_object = True 
            if comment not in inbox.posts.all():
                inbox.comments.add(comment)
        elif type_value == 'like':
            # TODO implement like
            pass
        if new_object:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)
        return Response(serializer.data, status=200)