from rest_framework import serializers
from django.http import HttpRequest
from post.models import Post, Like, Comment
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
        host_url = request.build_absolute_uri('/')
        url = f"{host_url}service/authors/{rep['id']}"
        rep['id'] = url
        rep['url'] = url

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
    class Meta:
        model = Post
        fields = '__all__'

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'