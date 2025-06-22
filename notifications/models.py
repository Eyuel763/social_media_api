from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')# The user who receives the notification
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='initiated_notifications')# The user who initiated the action (e.g., the user who liked a post)
    verb = models.CharField(max_length=255)# A short phrase describing the action (e.g., "liked", "commented on", "followed")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)# Generic foreign key to the object related to the notification (e.g., a Post, a Comment, a User)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey('content_type', 'object_id')
    timestamp = models.DateTimeField(auto_now_add=True)# Timestamp of when the notification was created
    is_read = models.BooleanField(default=False)# Boolean to track if the notification has been read

    class Meta:
        ordering = ['-timestamp'] # Order by newest first

    def __str__(self):
        return f"{self.actor.username} {self.verb} {self.target} (to {self.recipient.username})"
