from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Post(models.Model):
    body = models.TextField()
    shared_body = models.TextField(null=True , blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    shared_at = models.DateTimeField(null=True , blank=True)
    auther = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_user = models.ForeignKey(User, on_delete=models.CASCADE ,null =True ,blank=True ,related_name="+")
    likes = models.ManyToManyField(User, blank=True, related_name="likes")
    dislikes = models.ManyToManyField(User, blank=True, related_name="dislikes")
    image = models.ManyToManyField('Image', blank=True)

    tags = models.ManyToManyField('Tag', blank=True)
    def create_tags(self):
        for word in self.body.split():
            if(word[0] == '#'):
                tag = Tag.objects.filter(name=word[1:]).first()
                if tag:
                    self.tags.add(tag.pk)
                else:
                    tag= Tag(name=word[1:])
                    tag.save()
                    self.tags.add(tag.pk)
                self.save()        
                
        if self.shared_body:
            for word in self.shared_body.split():
                if (word[0] == '#'):
                    tag = Tag.objects.filter(name=word[1:]).first()
                    if tag:
                        self.tags.add(tag.pk)
                    else:
                        tag=Tag(name=word[1:])
                        tag.save()
                        self.tags.add(tag.pk)
                    self.save()                
        

    class Meta:
        ordering = ['-created_at' , 'shared_at']
        

class Comment(models.Model):
        comment = models.TextField()
        created_at = models.DateTimeField(default=timezone.now)
        author = models.ForeignKey(User, on_delete=models.CASCADE)
        post = models.ForeignKey(Post, on_delete=models.CASCADE)
        likes = models.ManyToManyField(User, blank=True, related_name="like")
        dislikes = models.ManyToManyField(User, blank=True, related_name="dislike")
        parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='+')

        tags = models.ManyToManyField('Tag', blank=True)

        def create_tags(self):
            for word in self.comment.split():
                if (word[0] == '#'):
                    tag = Tag.objects.get(name=word[1:])
                    if tag:
                        self.tags.add(tag.pk)
                    else:
                        tag = Tag(name=word[1:])
                        tag.save()
                        self.tags.add(tag.pk)
                    self.save()
            
                
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
    # 1 = Like, 2 = Comment, 3 = Follow , 4 = DM
    notification_type = models.IntegerField()
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='notifications_to')
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='notifications_from')
    date = models.DateTimeField(default=timezone.now)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    thread = models.ForeignKey('ThreadModel', on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    user_has_seen = models.BooleanField(default=False)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()


class Image(models.Model):
    image = models.ImageField(upload_to='media/uploads/post_picture', blank=True, null=True)


class ThreadModel(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
	receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')

class MessageModel(models.Model):
	thread = models.ForeignKey('ThreadModel', related_name='+', on_delete=models.CASCADE, blank=True, null=True)
	sender_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
	receiver_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
	body = models.CharField(max_length=1000)
	image = models.ImageField(upload_to='media/uploads/message_photos', blank=True, null=True)
	date = models.DateTimeField(default=timezone.now)
	is_read = models.BooleanField(default=False)


class Tag(models.Model):
	name = models.CharField(max_length=255)    