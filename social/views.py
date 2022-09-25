from cProfile import Profile
from multiprocessing import context
from django.shortcuts import render ,redirect
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from .models import *
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
        
        
        context = {
            'posts': posts,
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
        posts = Post.objects.all().order_by('-created_at')
        form = PostForm(request.POST)

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.auther = request.user
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

        comment = Comment.objects.filter(post=post).order_by('-created_at')        

        context = {
            'post': post,
            'form': form,
            'comment': comment,
        }
        return render(request , 'social/post_detail.html', context)

    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()

        comment = Comment.objects.filter(post=post).order_by('-created_at')
        context = {
            'post': post,
            'form': form,
            'comment': comment,
        }
        return render(request , 'social/post_detail.html', context)



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


class ProfileView(View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        user = profile.user
        posts = Post.objects.filter(auther=user).order_by('-created_at')

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
