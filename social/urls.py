from django.urls import path
from .views import *

urlpatterns = [
    path('', PostListView.as_view(),name='post-list'),
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

    path('profile/edit/<int:pk>/', ProfileEditView.as_view(),name='profile-edit'),
    path('profile/<int:pk>/followers/add', AddFollower.as_view(),name='add-follower'),
    path('profile/<int:pk>/followers/delete', RemoveFollower.as_view(),name='delete-follower'),
    path('search/', UserSearch.as_view(),name='search'),
    path('profile/<int:pk>/followers/', ListFollowers.as_view(),name='list-followers'),
    

]