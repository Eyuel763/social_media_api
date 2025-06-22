from rest_framework import serializers
from .models import Post, Comment, Like
from accounts.serializers import UserSerializer # Import UserSerializer for nested representation

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at', 'updated_at']
        read_only_fields = ['author', 'post', 'created_at', 'updated_at'] # Post and author set by view, not direct input

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    likes_count = serializers.SerializerMethodField() 
    is_liked_by_current_user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'content', 'created_at', 'updated_at', 'likes_count', 'is_liked_by_current_user']
        read_only_fields = ['author', 'created_at', 'updated_at'] # Author set by view

    def get_likes_count(self, obj):
        # Returns the total number of likes for the post
        return obj.likes.count()

    def get_is_liked_by_current_user(self, obj):
        # Checks if the authenticated user has liked this post
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False