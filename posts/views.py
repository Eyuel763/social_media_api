from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly # Custom permission

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
        # Set the author of the comment to the current authenticated user
        # And associate the comment with a specific post (if nested)
        post_id = self.kwargs.get('post_pk')
        if post_id:
            try:
                post = Post.objects.get(pk=post_id)
                serializer.save(author=self.request.user, post=post)
            except Post.DoesNotExist:
                raise serializers.ValidationError("Post not found.")
        else:
            # If not nested, ensure 'post' field is provided in the request data
            serializer.save(author=self.request.user)