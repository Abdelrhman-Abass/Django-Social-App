from django.contrib import admin
from  .models import *
# Register your models here.


admin.site.register(Post)
admin.site.register(UserProfile)
admin.site.register(Comment)
admin.site.register(Notifications)
admin.site.register(Image)
admin.site.register(ThreadModel)
admin.site.register(Tag)


