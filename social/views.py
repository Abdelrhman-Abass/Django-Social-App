from django.shortcuts import render ,redirect
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect , HttpResponse
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from django.utils import timezone
from .models import *
from django.contrib import messages
from django.views.generic.edit import *
from .forms import *
from django.db.models import Q
# Create your views here.

class PostListView(View):

    def get(self, request, *args, **kwargs):
        logged_in_user = request.user
        posts = Post.objects.filter(
            auther__profile__followers__in=[logged_in_user.id]
        ).order_by('-created_at')
        shared_form = ShareForm()
        
        context = {
            'posts': posts,
            'shared_form':shared_form,
        }
        return render(request , 'social/post_list.html', context)


class AddPostForm(LoginRequiredMixin ,View):
    def get(self, request, *args, **kwargs):
        form = PostForm()
        context = {
            'form': form,
        }
        return render(request , 'social/add_post.html',context)

    def post(self, request, *args, **kwargs):
        logged_in_user = request.user
        posts = Post.objects.filter(
            auther__profile__followers__in=[logged_in_user.id] 
        ).order_by('-created_at')
        form = PostForm(request.POST , request.FILES)
        files = request.FILES.getlist('image')

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.auther = request.user
            new_post.save()

            new_post.create_tags()

            for f in files:
                img = Image(image=f)
                img.save()
                new_post.image.add(img)

            new_post.save()

        context = {
            'posts': posts,
            'form': form,
            
        }
        return render(request , 'social/post_list.html', context)

class PostDetailView(LoginRequiredMixin , View):
    def get(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm()
        shared_form = ShareForm()

        comment = Comment.objects.filter(post=post).order_by('-created_at')        

        context = {
            'post': post,
            'form': form,
            'comment': comment,
            'shared_form':shared_form,
        }
        return render(request , 'social/post_detail.html', context)

    def post(self, request, pk, *args, **kwargs):
        logged_in_user = request.user
        post = Post.objects.filter(
            auther__profile__followers__in=[logged_in_user.id]
        )
        
        form = CommentForm(request.POST)
        shared_form = ShareForm()

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()

            new_comment.create_tags()

        comment = Comment.objects.filter(post=post).order_by('-created_at')
        notification = Notifications.objects.create(notification_type=2, user_from=request.user, user_to=post.auther, post=post)


        context = {
            'post': post,
            'form': form,
            'comment': comment,
            'shared_form':shared_form,
        }
        return render(request , 'social/post_detail.html', context)

class SharedPostView(View):
    def post(self, request, pk ,*args, **kwargs):
        original_post = Post.objects.get(pk=pk)
        form = ShareForm(request.POST)

        if form.is_valid():
            new_post = Post(
                shared_body=self.request.POST.get('body'),
                body=original_post.body,
                auther=original_post.auther,
                created_at=original_post.created_at,
                shared_user=request.user,
                shared_at=timezone.now(),
            )
            new_post.save()

            for img in original_post.image.all():
                new_post.add(img)
            new_post.save()
        
        return redirect('post-list') 



class PostEditView(LoginRequiredMixin,UserPassesTestMixin ,UpdateView):
    model = Post
    fields = ['body']
    template_name = 'social/post_edit.html'
    
    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('post_detail', kwargs={'pk': pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.auther


class CommentEditView(LoginRequiredMixin,UserPassesTestMixin ,UpdateView):
    model = Comment
    fields = ['comment']
    template_name = 'social/comment_edit.html'
    
    def get_success_url(self):
        pk = self.kwargs['post_pk']
        return reverse_lazy('post_detail', kwargs={'pk': pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

        

class PostDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Post
    template_name = 'social/post_delete.html'

    success_url = reverse_lazy('post-list')
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.auther

class CommentDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Comment
    template_name = 'social/comment_delete.html'

    def get_success_url(self):
        pk = self.kwargs['post_pk']
        return reverse_lazy('post_detail', kwargs={'pk': pk})

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

class CommentReplyView(LoginRequiredMixin, View):

    def post(self, request, post_pk, pk, *args, **kwargs):
        post = Post.objects.get(pk=post_pk)
        parent_comment = Comment.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.parent = parent_comment
            new_comment.save()

        notification = Notifications.objects.create(notification_type=2, user_from=request.user, user_to=parent_comment.author, comment=new_comment)

        return redirect('post_detail', pk=post_pk)


class ProfileView(View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        user = profile.user
        posts = Post.objects.filter(auther=user)

        followers = profile.followers.all()
        if len(followers) == 0:
            is_following = False

        for follower in followers:
            if follower == request.user:
                is_following = True
                break
            else:
                is_following = False



        number_of_followers = len(followers)

        context = {
            'user': user,
            'profile': profile,
            'posts': posts,
            'number_of_followers':number_of_followers,
            'is_following': is_following,
        }

        return render(request, 'social/profile.html', context)



class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserProfile
    fields = ['name', 'bio', 'birth', 'location', 'picture']
    template_name = 'social/profile_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile', kwargs={'pk': pk})

    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user

class AddFollower(LoginRequiredMixin, View):
    def post(self, request,pk, *args, **kwargs):
        profile =UserProfile.objects.get(pk=pk)
        profile.followers.add(request.user)
        notification = Notifications.objects.create(notification_type=3, user_from=request.user, user_to=profile.user)

        return redirect('profile',pk=profile.pk)


class RemoveFollower(LoginRequiredMixin, View):
    def post(self, request,pk, *args, **kwargs):
        profile =UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user)

        return redirect('profile',pk=profile.pk)


class AddLike(LoginRequiredMixin,View):
    def post(self, request,pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)

        is_dislike = False

        for  dislike in post.dislikes.all():
            if request.user == dislike:
                is_dislike = True
                break
        
        if is_dislike:
            post.dislikes.remove(request.user)


        is_like = False

        for  like in post.likes.all():
            if request.user == like:
                is_like = True
                break

        if not is_like:
            post.likes.add(request.user)
            notification = Notifications.objects.create(notification_type=1, user_from=request.user, user_to=post.auther, post=post)


        if is_like:
            post.likes.remove(request.user)

        next = request.POST.get('next','/')
        return HttpResponseRedirect(next)

class DisLike(LoginRequiredMixin,View):
    def post(self, request,pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)

        is_like = False

        for  like in post.likes.all():
            if request.user == like:
                is_like = True
                break
        if is_like:
            post.likes.remove(request.user)


        is_dislike = False

        for  dislike in post.dislikes.all():
            if request.user == dislike:
                is_dislike = True
                break

        if not is_dislike:
            post.dislikes.add(request.user)
            

        if is_dislike:
            post.dislikes.remove(request.user)

        next = request.POST.get('next','/')
        return HttpResponseRedirect(next)

class UserSearch(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        profile_list = UserProfile.objects.filter(
            Q(user__username__icontains=query)
        )
        context = {'profile_list': profile_list}
        return render(request, 'social\search.html', context)


class CommentDisLikes(LoginRequiredMixin, View):
    def post(self, request,pk, *args, **kwargs):
        comment = Comment.objects.get(pk=pk)
        
        is_like = False

        for  like in comment.likes.all():
            if request.user == like:
                is_like = True
                break
        if is_like:
            comment.likes.remove(request.user)


        is_dislike = False

        for  dislike in comment.dislikes.all():
            if request.user == dislike:
                is_dislike = True
                break

        if not is_dislike:
            comment.dislikes.add(request.user)

        if is_dislike:
            comment.dislikes.remove(request.user)

        next = request.POST.get('next','/')
        return HttpResponseRedirect(next)


class CommentLikes(LoginRequiredMixin, View):
    def post(self, request,pk, *args, **kwargs):
        comment = Comment.objects.get(pk=pk)
        is_dislike = False

        for  dislike in comment.dislikes.all():
            if request.user == dislike:
                is_dislike = True
                break
        
        if is_dislike:
            comment.dislikes.remove(request.user)


        is_like = False

        for  like in comment.likes.all():
            if request.user == like:
                is_like = True
                break

        if not is_like:
            comment.likes.add(request.user)
            notification = Notifications.objects.create(notification_type=1, user_from=request.user, user_to=comment.author, comment=comment)


        if is_like:
            comment.likes.remove(request.user)

        next = request.POST.get('next','/')
        return HttpResponseRedirect(next)



class ListFollowers(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs): 
        profile = UserProfile.objects.get(pk=pk)
        followers = profile.followers.all()


        number_of_followers = len(followers)
        context = {'profile':profile,'followers':followers}


        return render(request, 'social/followers.html', context)

class PostNotification(View):
    def get(self, request, notification_pk, post_pk, *args, **kwargs):
        notification = Notifications.objects.get(pk=notification_pk)
        post = Post.objects.get(pk=post_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('post_detail', pk=post_pk)

class FollowNotification(View):
    def get(self, request, notification_pk, profile_pk, *args, **kwargs):
        notification = Notifications.objects.get(pk=notification_pk)
        profile = UserProfile.objects.get(pk=profile_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('profile', pk=profile_pk)

class ThreadNotification(View):
    def get(self, request, notification_pk, object_pk, *args, **kwargs):
        notification = Notifications.objects.get(pk=notification_pk)
        thread = ThreadModel.objects.get(pk=object_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('thread', pk=object_pk)

class RemoveNotification(View):
    def delete(self, request, notification_pk, *args, **kwargs):
        notification = Notifications.objects.get(pk=notification_pk)

        notification.user_has_seen = True
        notification.save()

        return HttpResponse('Success', content_type='text/plain')

class ListThreads(View):
    def get(self, request, *args, **kwargs):
        threads = ThreadModel.objects.filter(Q(user=request.user) | Q(receiver=request.user))

        context = {
            'threads': threads
        }

        return render(request, 'social/inbox.html', context)

class CreateThread(View):
    def get(self, request, *args, **kwargs):
        form = ThreadForm()

        context = {
            'form': form
        }

        return render(request, 'social/create_thread.html', context)

    def post(self, request, *args, **kwargs):
        form = ThreadForm(request.POST)

        username = request.POST.get('username')

        try:
            receiver = User.objects.get(username=username)
            if ThreadModel.objects.filter(user=request.user, receiver=receiver).exists():
                thread = ThreadModel.objects.filter(user=request.user, receiver=receiver)[0]
                return redirect('thread', pk=thread.pk)
            elif ThreadModel.objects.filter(user=receiver, receiver=request.user).exists():
                thread = ThreadModel.objects.filter(user=receiver, receiver=request.user)[0]
                return redirect('thread', pk=thread.pk)

            if form.is_valid():
                thread = ThreadModel(
                    user=request.user,
                    receiver=receiver
                )
                thread.save()

                return redirect('thread', pk=thread.pk)
        except:
            messages.error(request, 'Invalid username')
            return redirect('create-thread')

class ThreadView(View):
    def get(self, request, pk, *args, **kwargs):
        form = MessageForm()
        thread = ThreadModel.objects.get(pk=pk)
        message_list = MessageModel.objects.filter(thread__pk__contains=pk)
        context = {
            'thread': thread,
            'form': form,
            'message_list': message_list
        }

        return render(request, 'social/thread.html', context)

class CreateMessage(View):
    def post(self, request, pk, *args, **kwargs):
        form = MessageForm(request.POST, request.FILES)
        
        thread = ThreadModel.objects.get(pk=pk)
        if thread.receiver == request.user:
            receiver = thread.user
        else:
            receiver = thread.receiver

        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.sender_user = request.user
            message.receiver_user = receiver
            message.save()

        notification = Notifications.objects.create(
            notification_type=4,
            user_from=request.user,
            user_to=receiver,
            thread=thread
        )
        return redirect('thread', pk=pk)            

class Explore(View):
    def get(self, request,*args, **kwargs):
        exploreForm = ExploreForm()
        query = self.request.GET.get('query')
        tag = Tag.objects.filter(name=query).first()
        if tag:
            posts = Post.objects.filter(tags__in=[tag]) 
        else:
            posts = Post.objects.all() 

        context={'tag':tag , 'pos':posts , 'explore_Form':exploreForm}       
        return render(request,'social/explore.html' , context)

    def post(self, request,*args, **kwargs):
        exploreForm = ExploreForm(request.POST)
        if exploreForm.is_valid():
            query = exploreForm.cleaned_data['query']
            tag = Tag.objects.filter(name=query).first()

            posts = None
            if tag:
                posts = Post.objects.filter(tags__in=[tag])

            if posts:
                context={
                    'tag':tag,
                    'pos':posts,
                }
            else:
                context={
                    'tag':tag,
                }
            return  HttpResponseRedirect(f'?query={query}')
        return  HttpResponseRedirect(f'explore/')    
            
