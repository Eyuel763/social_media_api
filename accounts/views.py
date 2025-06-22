from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.contenttypes.models import ContentType
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer
from .models import User
from notifications.models import Notification

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "user": UserSerializer(user).data,
            "token": token.key
        }, status=status.HTTP_201_CREATED)

class UserLoginView(ObtainAuthToken):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

class UserFollowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, format=None):
        # Get the user to be followed
        user_to_follow = get_object_or_404(User, pk=pk)
        # Get the authenticated user who wants to follow
        current_user = request.user

        if current_user == user_to_follow:
            return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        # Add user_to_follow to the current_user's 'following' list.
        # 'following' is the related_name for the reverse relationship of 'followers' field on User model.
        if user_to_follow not in current_user.following.all():
            current_user.following.add(user_to_follow)

            # Create notification for the user who was followed
            Notification.objects.create(
                recipient=user_to_follow, # User being followed receives notification
                actor=current_user, # User who initiated the follow
                verb='followed you',
                target=current_user # Target is the user who followed
            )
            return Response({"detail": f"You are now following {user_to_follow.username}."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": f"You are already following {user_to_follow.username}."}, status=status.HTTP_409_CONFLICT)

class UserUnfollowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, format=None):
        # Get the user to be unfollowed
        user_to_unfollow = get_object_or_404(User, pk=pk)
        # Get the authenticated user who wants to unfollow
        current_user = request.user

        if current_user == user_to_unfollow:
            return Response({"detail": "You cannot unfollow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        # Remove user_to_unfollow from the current_user's 'following' list.
        if user_to_unfollow in current_user.following.all():
            current_user.following.remove(user_to_unfollow)
            return Response({"detail": f"You have unfollowed {user_to_unfollow.username}."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": f"You are not following {user_to_unfollow.username}."}, status=status.HTTP_409_CONFLICT) # 409 Conflict if not following