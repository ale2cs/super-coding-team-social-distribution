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

    def get_type(self, obj):
        return 'author'
    
    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            host_url = request.build_absolute_uri('/')[:-1]
            url = request.path.rstrip('followers/')
            return f'{host_url}{url}'
            
        return ''
    
    def get_host(self, obj):
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

    def get_type(self, obj):
        return 'post'

    def get_source(self, obj):
        return ''

    def get_origin(self, obj):
        return ''

    def get_count(self, obj):
        return 0
    
    def to_representation(self, obj):
        rep = super().to_representation(obj)
        request = self.context.get('request')
        if request:
            profile_serializer = ProfileSerializer(obj.author, context={'request': request})
            rep['author'] = profile_serializer.data
            path = request.build_absolute_uri()
            rep['id'] = f'{path}/{obj.id}'
            rep['source'] = path
            rep['origin'] = path
        _, comment_count = obj.get_comments()
        rep['count'] = comment_count
        rep['categories'] = [category.name for category in obj.categories.all()]
        return rep

    class Meta:
        model = Post
        fields = ['type', 'title', 'id', 'source', 'origin', 'description', 'contentType', 'content', 'author', 'categories', 'count', 'published', 'visibility', 'unlisted']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'