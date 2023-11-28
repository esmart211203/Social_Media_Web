from django.contrib import admin
from .models import (
    Post,
    Comment,
    React,
    UserProfileInfo,
    GroupRequest,
    FriendRequest,
    FriendList,
    Group,
    GroupMember,
    Block,
    Province,
    Page,
    PersonalInformation,
    Favorites,
    ChatMessage,
    Notification,
)

# Register your models here.

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(React)
admin.site.register(UserProfileInfo)
admin.site.register(FriendRequest)
admin.site.register(FriendList)
admin.site.register(GroupMember)
admin.site.register(Group)
admin.site.register(GroupRequest)
admin.site.register(Block)
admin.site.register(Province)
admin.site.register(Page)
admin.site.register(PersonalInformation)
admin.site.register(Favorites)
admin.site.register(ChatMessage)
admin.site.register(Notification)
