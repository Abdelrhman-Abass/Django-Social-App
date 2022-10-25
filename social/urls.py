from django.urls import path
from .views import *

urlpatterns = [
    path('', PostListView.as_view(),name='post-list'),
    path('explore/',Explore.as_view(),name='explore'),
    path('add/', AddPostForm.as_view(),name='add'),
    path('detail/<int:pk>/', PostDetailView.as_view(),name='post_detail'),
    path('edit/<int:pk>/', PostEditView.as_view(),name='post-edit'),
    path('delete/<int:pk>/', PostDeleteView.as_view(),name='post-delete'),
    path('<int:post_pk>/comment/delete/<int:pk>/', CommentDeleteView.as_view(),name='comment-delete'),
    path('<int:post_pk>/comment/edit/<int:pk>/', CommentEditView.as_view(),name='comment-edit'),
    path('profile/<int:pk>', ProfileView.as_view(),name='profile'),
    path('<int:pk>/like/', AddLike.as_view(),name='add-like'),
    path('<int:pk>/dislike/', DisLike.as_view(),name='dislike'),
    path('<int:pk>/comment/likes/', CommentLikes.as_view(),name='comment-likes'),
    path('<int:pk>/comment/dislikes/', CommentDisLikes.as_view(),name='comment-dislikes'),
    path('<int:post_pk>/comment/<int:pk>/reply/', CommentReplyView.as_view(),name='comment-reply'),
    path('<int:pk>/shared/post/',SharedPostView.as_view(),name='shared-post'),

    path('profile/edit/<int:pk>/', ProfileEditView.as_view(),name='profile-edit'),
    path('profile/<int:pk>/followers/add', AddFollower.as_view(),name='add-follower'),
    path('profile/<int:pk>/followers/delete', RemoveFollower.as_view(),name='delete-follower'),
    path('search/', UserSearch.as_view(),name='search'),
    path('profile/<int:pk>/followers/', ListFollowers.as_view(),name='list-followers'),
    
    path('notification/<int:notification_pk>/post/<int:post_pk>/', PostNotification.as_view(),name='post-notification'),
    path('notification/<int:notification_pk>/post/<int:profile_pk>/', FollowNotification.as_view(),name='follow-notification'),
    path('notification/<int:notification_pk>/thread/<int:object_pk>', ThreadNotification.as_view(), name='thread-notification'),
    path('notification/delete/<int:notification_pk>', RemoveNotification.as_view(), name='notification-delete'),
    
    path('inbox/', ListThreads.as_view(), name='inbox'),
    path('inbox/create-thread/', CreateThread.as_view(), name='create-thread'),
    path('inbox/<int:pk>/', ThreadView.as_view(), name='thread'),
    path('inbox/<int:pk>/create-message/', CreateMessage.as_view(), name='create-message'),
]