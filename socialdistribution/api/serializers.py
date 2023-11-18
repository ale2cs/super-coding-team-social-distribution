from rest_framework import serializers
from django.http import HttpRequest
from post.models import Post, Like, Comment, Category
from author.models import Profile, Follower

class ProfileSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    host = serializers.SerializerMethodField()
    displayName = serializers.CharField(source='user.username')
    profileImage = serializers.URLField(source='avatar')

    def get_type(self, instance):
        return 'author'
    
    def get_url(self, instance):
        request = self.context.get('request')
        if request:
            host_url = request.build_absolute_uri('/')[:-1]
            url = request.path.rstrip('followers/')
            return f'{host_url}{url}'
            
        return ''
    
    def get_host(self, instance):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri('/')
        return ''

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        if request:
            host_url = request.build_absolute_uri('/')
            url = f"{host_url}service/authors/{rep['id']}"
            rep['id'] = url
            rep['url'] = url
        else:
            rep['id'] = ''
            rep['url'] = ''

        git = rep['github']
        if git != '':
            rep['github'] = f"https://github.com/{git}"
        else:
            rep['github'] = ''
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
            rep['id'] = f'{host}service/authors/{instance.author_id}/posts/{instance.id}'
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
    class Meta:
        model = Like
        fields = '__all__'
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