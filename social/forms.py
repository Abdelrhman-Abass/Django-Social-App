from dataclasses import fields
from logging import PlaceHolder
from pyexpat import model
from django import forms

from .models import *

class PostForm(forms.ModelForm):
    body = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows':3,
            'placeholder' : 'Say Something...'
            }))

    class Meta:
        model = Post
        fields = ['body',]

class CommentForm(forms.ModelForm):
    comment = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows':3,
            'placeholder' : 'Say Something...'
            }))

    class Meta:
        model = Comment
        fields = ['comment',]



