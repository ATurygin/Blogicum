from django import forms
from django.contrib.auth.forms import UserChangeForm

from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author', 'created_at')
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            )
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class ProfileForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        fields = ('username', 'first_name',
                  'last_name', 'email')
