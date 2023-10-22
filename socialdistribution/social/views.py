import json
from django.shortcuts import render
from django.http import HttpResponse
from django.db import models
from rest_framework.views import APIView
from .models import Post, Author
from .serializers import PostSerializer
from rest_framework.response import Response

# Create your views here.
def index(request):
    return HttpResponse("Social index")

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
        posts = Post.objects.filter(models.Q(author__id=kwargs['author_id'])).order_by('-published')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=201)
        
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