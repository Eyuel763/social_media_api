from rest_framework import viewsets, permissions, filters, status
from rest_framework.pagination import PageNumberPagination
from .models import Post, Comment, Like
from notifications.models import Notification # Import Notification model
from .serializers import PostSerializer, CommentSerializer
from rest_framework.response import Response
from .permissions import IsOwnerOrReadOnly # Custom permission
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView # For Like/Unlike actions
from django_filters.rest_framework import DjangoFilterBackend
from django.db import IntegrityError # To handle unique_together constraint
from django.shortcuts import get_object_or_404

class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsPagination # Apply pagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter] # Apply filtering
    search_fields = ['title', 'content', 'author__username'] # Fields to search by
    ordering_fields = ['created_at', 'title'] # Fields to order by
    ordering = ['-created_at'] # Default ordering

    def get_serializer_context(self):
        return {'request': self.request}# Pass the request to the serializer context for `is_liked_by_current_user`

    def perform_create(self, serializer):
        # Set the author of the post to the current authenticated user
        serializer.save(author=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsPagination # Apply pagination

    def get_queryset(self):
        # Allow filtering comments by post ID if a 'post_pk' is provided in the URL
        # This is typically handled by nested routers or by passing 'post' in the URL
        if 'post_pk' in self.kwargs:
            return self.queryset.filter(post=self.kwargs['post_pk'])
        return self.queryset

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_pk')
        if post_id:
            try:
                post = get_object_or_404(Post, pk=post_id)
                comment = serializer.save(author=self.request.user, post=post)

                # Create notification for the post author
                if post.author != self.request.user: # Don't notify if commenting on own post
                    Notification.objects.create(
                        recipient=post.author,
                        actor=self.request.user,
                        verb='commented on',
                        target=comment 
                    )
            except Post.DoesNotExist:
                raise serializers.ValidationError({"detail": "Post not found."})
        else:
            raise serializers.ValidationError({"detail": "Post ID is required to create a comment."})

class UserFeedView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated] # Only authenticated users can see their feed
    pagination_class = StandardResultsPagination # Apply pagination to the feed
    
    def get_queryset(self):
        user = self.request.user
        # Get all users that the current user is following
        # 'following' is the related_name on the 'followers' ManyToMany field in the User model
        followed_users = user.following.all()
        
        # Combine the followed users with the current user to create a feed
        combined_users = list(followed_users) + [user] # Include the current user in the feed
        
        # Filter posts where the author is one of the followed users
        # Order by created_at in descending order (most recent first)
        queryset = Post.objects.filter(author__in=combined_users).order_by('-created_at')
        return queryset
    
class PostLikeUnlikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, format=None):
        post = get_object_or_404(Post, pk=pk)
        user = request.user

        # Try to create a Like object
        try:
            Like.objects.create(user=user, post=post)
            # Create notification for the post author
            if post.author != user: # Don't notify if liking your own post
                Notification.objects.create(
                    recipient=post.author,
                    actor=user,
                    verb='liked',
                    target=post
                )
            return Response({"detail": "Post liked successfully."}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"detail": "You have already liked this post."}, status=status.HTTP_409_CONFLICT) # Conflict if already liked

    def delete(self, request, pk, format=None):
        post = get_object_or_404(Post, pk=pk)
        user = request.user

        # Try to delete the Like object
        try:
            like = Like.objects.get(user=user, post=post)
            like.delete()
            # Optional: Remove corresponding notification if desired. This can be complex if a user has multiple likes
            # or if the notification is for general likes. For simplicity, we're just deleting the Like object.
            return Response({"detail": "Post unliked successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            return Response({"detail": "You have not liked this post."}, status=status.HTTP_404_NOT_FOUND)