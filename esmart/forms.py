from django import forms
from django.contrib.auth.models import User
from .models import UserProfileInfo, Post, Comment, ChatMessage


####################### USER #######################
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ("username", "email", "password", "first_name", "last_name")


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfileInfo
        fields = ("profile_pic",)


class UpdateBioForm(forms.ModelForm):
    class Meta:
        model = UserProfileInfo
        fields = ("bio",)


####################### POST #######################
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("author", "content", "image", "status")


####################### Comment #######################
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("post", "author", "content")


class ChatMessageForm(forms.ModelForm):
    body = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "row": 3,
                "placeholder": "Viết gì đó đi",
            }
        )
    )

    class Meta:
        model = ChatMessage
        fields = ["body"]
