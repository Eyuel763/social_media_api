from django.db import models
from django.conf import settings # Import settings to get the AUTH_USER_MODEL

class Post(models.Model):
    # ForeignKey to the custom User model defined in the 'accounts' app
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at'] # Order posts by creation date, newest first

    def __str__(self):
        return f"{self.title} by {self.author.username}"

class Comment(models.Model):
    # ForeignKey to the Post model
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    # ForeignKey to the custom User model (author of the comment)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at'] # Order comments by creation date, oldest first

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title[:30]}..."
    
class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure a user can only like a specific post once
        unique_together = ('user', 'post')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"
