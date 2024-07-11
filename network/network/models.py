from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(upload_to='user_pfp', blank=True, null=True)
    followers = models.ManyToManyField(User, blank=True, related_name="following")
    following = models.ManyToManyField(User, blank=True, related_name="followers")

class Post(models.Model):
    post_by = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")
    message = models.TextField()
    likes = models.ManyToManyField(Profile, related_name='liked_posts')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def poster(self):
        return self.post_by.user.username

    def like_count(self):
        return self.likes.count()