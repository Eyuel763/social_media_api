from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView # For marking notifications as read

from .models import Notification
from .serializers import NotificationSerializer
from posts.views import StandardResultsPagination # Reuse pagination class

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsPagination

    def get_queryset(self):
        # Return notifications for the authenticated user, ordered by newest first
        return Notification.objects.filter(recipient=self.request.user).order_by('-timestamp')

class NotificationMarkAsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, format=None):
        # Mark a specific notification as read
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
            notification.is_read = True
            notification.save()
            return Response({"detail": "Notification marked as read."}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"detail": "Notification not found or you don't have permission."}, status=status.HTTP_404_NOT_FOUND)

class MarkAllNotificationsAsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        # Mark all unread notifications for the current user as read
        notifications_updated = Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({"detail": f"{notifications_updated} notifications marked as read."}, status=status.HTTP_200_OK)
