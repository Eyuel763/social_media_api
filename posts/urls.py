from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import PostViewSet, CommentViewSet, UserFeedView, PostLikeUnlikeView

# Create a default router for posts
router = DefaultRouter()
router.register(r'posts', PostViewSet)

# Create a nested router for comments under posts
# This allows URLs like /posts/{post_pk}/comments/
posts_router = routers.NestedSimpleRouter(router, r'posts', lookup='post')
posts_router.register(r'comments', CommentViewSet, basename='post-comments')

urlpatterns = [
    path('', include(router.urls)), # Includes /posts/
    path('', include(posts_router.urls)), # Includes /posts/{post_pk}/comments/
    path('feed/', UserFeedView.as_view(), name='user-feed'),
    path('posts/<int:pk>/like/', PostLikeUnlikeView.as_view(), name='post-like'),
    path('posts/<int:pk>/unlike/', PostLikeUnlikeView.as_view(), name='post-unlike'), # DELETE method for unlike
]