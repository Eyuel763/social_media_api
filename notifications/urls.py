from django.urls import path
from .views import NotificationListView, NotificationMarkAsReadView, MarkAllNotificationsAsReadView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/mark_as_read/', NotificationMarkAsReadView.as_view(), name='notification-mark-as-read'),
    path('mark_all_as_read/', MarkAllNotificationsAsReadView.as_view(), name='notifications-mark-all-as-read'),
]