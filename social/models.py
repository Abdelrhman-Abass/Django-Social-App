from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Post(models.Model):
    body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    auther = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, blank=True, related_name="likes")
    dislikes = models.ManyToManyField(User, blank=True, related_name="dislikes")
    image = models.ImageField(upload_to='media/uploads/post_picture', blank=True, null=True)

class Comment(models.Model):
        comment = models.TextField()
        created_at = models.DateTimeField(default=timezone.now)
        author = models.ForeignKey(User, on_delete=models.CASCADE)
        post = models.ForeignKey(Post, on_delete=models.CASCADE)
        likes = models.ManyToManyField(User, blank=True, related_name="like")
        dislikes = models.ManyToManyField(User, blank=True, related_name="dislike")
        parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='+')

        @property
        def children(self):
            return Comment.objects.filter(parent=self).order_by('-created_at').all()

        @property
        def is_parent(self):
            if self.parent is None:
                return True
            return False



class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True , verbose_name="user" , related_name="profile", on_delete=models.CASCADE)
    name = models.CharField(max_length=40,blank=True, null=True)
    bio = models.TextField(max_length=200, blank=True, null=True)
    birth = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    picture = models.ImageField(upload_to='media/uploads/profile_pictures', default='media/media/uploads/profile_pictures/default.png', blank=True)
    followers = models.ManyToManyField(User,blank=True , related_name='followers')


    @property
    def imageURL(self):
        if self.picture:
            return self.picture.url
        else:
            return 'media/media/uploads/profile_pictures/default.png'

class Notifications(models.Model):
    # 1 = Like, 2 = Comment, 3 = Follow
    notification_type = models.IntegerField()
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='notifications_to')
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='notifications_from')
    date = models.DateTimeField(default=timezone.now)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    user_has_seen = models.BooleanField(default=False)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()