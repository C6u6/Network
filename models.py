from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    creator = models.ForeignKey("network.User", on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    likes = models.IntegerField(default=0, null=True)

    def __str__(self):
        return f"{self.creator}: {self.content}"

    def all_data(self):
        return {'creator': self.creator, 'content': self.content, 'created_at': self.created_at, 'updated_at': self.updated_at, 'likes': self.likes}

    def is_valid(self):
        valid_creator = self.creator is not None
        valid_content = len(self.content) > 0
        valid_time = self.created_at != self.updated_at
        return valid_creator and valid_content and valid_time

class Following(models.Model):
    follower = models.ForeignKey("network.User", on_delete=models.CASCADE, related_name='following_set_launcher')
    following = models.ForeignKey("network.User", on_delete=models.CASCADE, related_name='following_set_target')

    def __str__(self):
        return f"{self.follower} is following {self.following}"

    def is_valid(self):
        return self.follower != self.following

class Likes(models.Model):
    user = models.ForeignKey("network.User", on_delete=models.CASCADE, related_name='likes_set_launcher')
    liked = models.ForeignKey("network.Post", on_delete=models.CASCADE, related_name='likes_set_target')

    def __str__(self):
        return f"{self.user} liked {self.liked}"

    def is_valid(self):
        return self.user is not None