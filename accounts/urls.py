from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserProfileView, UserFollowView, UserUnfollowView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('users/<int:pk>/follow/', UserFollowView.as_view(), name='follow-user'),
    path('users/<int:pk>/unfollow/', UserUnfollowView.as_view(), name='unfollow-user'),
]