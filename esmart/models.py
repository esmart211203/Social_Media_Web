# import modules
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.shortcuts import get_object_or_404
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.conf import settings
from django.urls import reverse
from django.db import models


# Create your models here.
class UserProfileInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to="profile_pic", blank=True)
    bio = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return self.user.username


class FriendRequest(models.Model):
    sender = models.ForeignKey(
        User, related_name="friend_requests_sent", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User, related_name="friend_requests_received", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)


class FriendList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    friends = models.ManyToManyField(User, related_name="friends")
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username

    def get_all_friends(self):
        return self.friends.all()

    def count_friends(self):
        return self.friends.count()

    def remove_friend(self, friend):
        self.friends.remove(friend)
        friend_list = FriendList.objects.filter(user=friend).first()
        if friend_list:
            friend_list.friends.remove(self.user)


####################### GROUP #######################
class Group(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    group_pic = models.ImageField(upload_to="group_pic", blank=True)
    status = models.CharField(
        max_length=20, choices=[("public", "Public"), ("private", "Private")]
    )
    admin = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="admin_groups"
    )

    def __str__(self):
        return str(self.name)


class GroupMember(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="members")
    member = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="member_groups"
    )

    def __str__(self):
        return str(self.group)

    def count_members(group_id):
        total_member = GroupMember.objects.filter(group=group_id).count()
        return total_member


class GroupRequest(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="requests")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="group_requests"
    )
    message = models.TextField()
    approved = models.BooleanField(default=False)

    def __str__(self):
        return str(self.group)


class Province(models.Model):
    slug = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Page(models.Model):
    name = models.CharField(max_length=100)
    category = models.TextField()
    description = models.TextField()
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE, related_name="province"
    )
    page_profile_pic = models.ImageField(upload_to="page_profile_pic", blank=True)
    admin = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="admin_page", null=True
    )

    def __str__(self):
        return str(self.name)


####################### POST #######################
class Post(models.Model):
    STATUS_CHOICES = (
        ("public", "Mọi người"),
        ("friend", "Bạn bè"),
        ("only_me", "Chỉ mình tôi"),
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to="posts", null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="public")
    page = models.ForeignKey(Page, blank=True, null=True, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content[:50]

    def count_posts(group_id):
        total_posts = Post.objects.filter(group=group_id).count()
        return total_posts

    def count_reacts(post_id):
        total_react = React.objects.filter(post=post_id).count()
        return total_react

    def count_comment(post_id):
        total_comment = Comment.objects.filter(post=post_id).count()
        return total_comment


####################### Comment #######################
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content

    def count_comments(post_id):
        total_comments = Comment.objects.filter(post_id=post_id).count()
        return total_comments


####################### Like #######################
class React(models.Model):
    STATUS_CHOICES = (
        ("like", "Thích"),
        ("favourite", "Yêu thích"),
        ("sad", "Buồn"),
        ("angry", "Phẫn nộ"),
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="like")

    def count_react(post_id):
        total_react = React.objects.filter(post_id=post_id).count()
        return total_react

    def __str__(self):
        return f"{self.author} react {self.post}"


class Block(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    block_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="block_user"
    )

    def __str__(self):
        return f"{self.user} blocked {self.block_user}"


class PersonalInformation(models.Model):
    SEX_CHOICES = (
        ("male", "Trai"),
        ("female", "Gái"),
        ("3rd_gender", "Giới tính thứ 3"),
        ("hidden", "Không tiết lộ"),
    )
    STATUS_CHOICES = (
        ("single", "Độc thân"),
        ("dating", "Hẹn hò"),
    )
    DEGREE_CHOICES = (
        ("none", "Không có"),
        ("high_school", "THPT"),
        ("college", "Cao đẳng"),
        ("university", "Đại học"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    home_town = models.ForeignKey(
        Province, on_delete=models.CASCADE, related_name="home_town", null=True
    )
    residence = models.ForeignKey(
        Province, on_delete=models.CASCADE, related_name="residence", null=True
    )
    sex = models.CharField(max_length=50, choices=SEX_CHOICES, null=True)
    relationship = models.CharField(max_length=50, choices=STATUS_CHOICES, null=True)
    degree = models.CharField(max_length=50, choices=DEGREE_CHOICES, null=True)
    workplace = models.ForeignKey(
        Page, on_delete=models.CASCADE, related_name="page", null=True
    )

    def __str__(self):
        return str(self.user)


class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True)
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="receiver", null=True
    )

    def __str__(self):
        return f"{self.user} favorites {self.page} or {self.receiver}"


class ChatMessage(models.Model):
    body = models.TextField()
    msg_sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="msg_sender"
    )
    msg_receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="msg_receiver"
    )
    img = models.ImageField(upload_to="chats", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.msg_sender} chat {self.msg_receiver}"

    def get_chat_messages(user, receiver):
        chat_messages = ChatMessage.objects.filter(
            (models.Q(msg_sender=user) & models.Q(msg_receiver=receiver))
            | (models.Q(msg_sender=receiver) & models.Q(msg_receiver=user))
        ).order_by("created_at")
        return chat_messages


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.CharField(max_length=100)
    is_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.user} notification {self.notification}"
