from rest_framework import serializers
from .models import Post, Author, Follower

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = '__all__'