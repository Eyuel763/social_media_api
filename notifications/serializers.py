from rest_framework import serializers
from .models import Notification
from accounts.serializers import UserSerializer # For actor/recipient details if needed
from posts.serializers import PostSerializer # To serialize target if it's a post
from posts.models import Post, Comment # For GenericForeignKey target resolution
from django.contrib.auth import get_user_model # For target if it's a user

User = get_user_model()

class NotificationSerializer(serializers.ModelSerializer):
    actor_username = serializers.ReadOnlyField(source='actor.username')
    target_info = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'actor_username', 'verb', 'target_info', 'timestamp', 'is_read']
        read_only_fields = ['recipient', 'actor_username', 'verb', 'target_info', 'timestamp']

    def get_target_info(self, obj):
        # Return a dictionary with relevant info about the target object
        if obj.target:
            if isinstance(obj.target, Post):
                return {
                    'type': 'Post',
                    'id': obj.target.id,
                    'title': obj.target.title,
                    'content_snippet': obj.target.content[:50] + '...' if len(obj.target.content) > 50 else obj.target.content
                }
            elif isinstance(obj.target, Comment):
                return {
                    'type': 'Comment',
                    'id': obj.target.id,
                    'content_snippet': obj.target.content[:50] + '...' if len(obj.target.content) > 50 else obj.target.content,
                    'post_title': obj.target.post.title
                }
            elif isinstance(obj.target, User):
                return {
                    'type': 'User',
                    'id': obj.target.id,
                    'username': obj.target.username,
                    'bio_snippet': obj.target.bio[:50] + '...' if obj.target.bio and len(obj.target.bio) > 50 else obj.target.bio
                }
            return {'type': obj.content_type.model, 'id': obj.object_id}
        return None