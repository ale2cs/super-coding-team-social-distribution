import requests
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet
from django.http import HttpRequest
from rest_framework.response import Response
from post.models import Post, Like, Comment, CommentLike, RemoteComment, RemoteLike
from author.models import Profile, Follower, FriendFollowRequest
from inbox.models import Inbox
from .services import get_author_from_link

class ProfileSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    host = serializers.SerializerMethodField()
    displayName = serializers.CharField(source='user.username')
    profileImage = serializers.URLField(source='avatar')

    def get_type(self, instance):
        return 'author'
    
    def get_url(self, instance):
        return ''
    
    def get_host(self, instance):
        return ''

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        if request:
            host = request.build_absolute_uri('/')
            url = f"{host}authors/{rep['id']}"
            rep['host'] = host
            rep['id'] = url
            rep['url'] = url
            rep['profileImage'] = f"{host}media/{rep['profileImage']}"

        if instance.github != '':
            rep['github'] = f"https://github.com/{instance.github}"
        return rep
    class Meta:
        model = Profile 
        fields = ['type', 'id', 'url', 'host', 'displayName', 'github', 'profileImage']

class PostSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    origin = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    def get_type(self, instance):
        return 'post'

    def get_source(self, instance):
        return ''

    def get_origin(self, instance):
        return ''

    def get_count(self, instance):
        return 0
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        if request:
            profile_serializer = ProfileSerializer(instance.author, context={'request': request})
            rep['author'] = profile_serializer.data
            path = request.build_absolute_uri()
            host = request.build_absolute_uri('/')
            rep['id'] = f'{host}authors/{instance.author_id}/posts/{instance.id}'
            rep['source'] = path
            rep['origin'] = path
        _, comment_count = instance.get_comments()
        rep['count'] = comment_count
        rep['categories'] = [category.name for category in instance.categories.all()]
        return rep

    class Meta:
        model = Post
        fields = ['type', 'title', 'id', 'source', 'origin', 'description', 'contentType', 'content', 'author', 'categories', 'count', 'published', 'visibility', 'unlisted']

class LikeSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    object = serializers.SerializerMethodField()

    def get_type(self, instance):
        return 'like'

    def get_object(self, instance):
        return ''

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        if request:
            post = instance.post
            author = post.author
            profile_serializer = ProfileSerializer(instance.author, context={'request': request})
            host = request.build_absolute_uri('/')
            rep['@context'] = 'https://www.w3.org/ns/activitystreams'
            rep['author'] = profile_serializer.data
            rep['object'] = f'{host}authors/{author.id}/posts/{post.id}'
        return rep

    class Meta:
        model = Like
        fields = ['type', 'summary', 'author', 'object']

class CommentLikeSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    object = serializers.SerializerMethodField()
    
    def get_type(self, instance):
        return 'like'

    def get_object(self, instance):
        return ''

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        if request:
            comment = instance.comment
            post = instance. comment.post
            author = comment.author
            profile_serializer = ProfileSerializer(instance.author, context={'request': request})
            host = request.build_absolute_uri('/')
            rep['@context'] = 'https://www.w3.org/ns/activitystreams'
            rep['author'] = profile_serializer.data
            rep['object'] = f'{host}authors/{author.id}/posts/{post.id}/comment/{comment.id}'
        return rep

    class Meta:
        model = CommentLike
        fields = ['type', 'summary', 'author', 'object'] 

class CommentSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    comment = serializers.CharField(source='content')

    def get_type(self, instance):
        return 'comment'

    def to_representation(self, instance):
        rep =  super().to_representation(instance)
        request = self.context.get('request')
        if request:
            serializer = ProfileSerializer(instance.author, context={'request': request})
            rep['author'] = serializer.data
            rep['id'] = f'{request.build_absolute_uri()}/{instance.id}'
        return rep

    class Meta:
        model = Comment
        fields = ['type', 'id', 'author', 'comment', 'contentType', 'published']

class FollowSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    actor = ProfileSerializer(source='follower', read_only=True)
    object = ProfileSerializer(source='followee', read_only=True)

    def get_type(self, instance):
        return 'follow'
    class Meta:
        model = FriendFollowRequest
        fields = ['type', 'summary', 'actor', 'object']
    

class ImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, instance):
        return ''

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        if instance.image_file:
            host = request.build_absolute_uri('/')
            rep['image'] = f'{host}media/{instance.image_file}'
        if instance.image_url:
            rep['image'] = f'{instance.image_url}'
        return rep
    class Meta:
        model = Post
        fields = ['image']

class InboxSerializer(serializers.ModelSerializer):
    '''
    Does not work, tried using get_serializer
    Using ModelSerializer instead of Serializer atm
    Tried ModelViewSet as well
    '''
    def to_representation(self, instance):
        request = self.context.get('request')
        type_value = request.data['type']
        if type_value == 'post':
            serializer = PostSerializer(instance, context={'request': request})
        elif type_value == 'follow':
            serializer = FollowSerializer(instance, context={'request': request})
        elif type_value == 'like':
            serializer = LikeSerializer(instance, context={'request': request})
        elif type_value == 'comment':
            serializer = CommentSerializer(instance, context={'request': request})
        return serializer.data
    
    class Meta:
        model = Inbox
        fields = '__all__'


class RemoteCommentSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    comment = serializers.CharField(source='content')

    def get_type(self, instance):
        return 'comment'

    def to_representation(self, instance):
        rep =  super().to_representation(instance)
        request = self.context.get('request')
        if request:

            rep['author'] = get_author_from_link(instance.author)
            rep['id'] = f'{request.build_absolute_uri()}/{instance.id}'
        return rep

    class Meta:
        model = Comment
        fields = ['type', 'id', 'author', 'comment', 'contentType', 'published']

class RemoteLikeSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    object = serializers.SerializerMethodField()

    def get_type(self, instance):
        return 'like'

    def get_object(self, instance):
        return ''

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        if request:
            post = instance.post
            author = post.author
            host = request.build_absolute_uri('/')
            rep['@context'] = 'https://www.w3.org/ns/activitystreams'
            rep['author'] = get_author_from_link(instance.author)
            rep['object'] = f'{host}authors/{author.id}/posts/{post.id}'
        return rep

    class Meta:
        model = Like
        fields = ['type', 'summary', 'author', 'object']