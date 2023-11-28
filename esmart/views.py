# import modules
import django.contrib.auth.models
from django.shortcuts import render, redirect, HttpResponse
from esmart.forms import (
    UserProfileForm,
    UserForm,
    PostForm,
    CommentForm,
    UpdateBioForm,
    ChatMessageForm,
)
from django.contrib.auth import authenticate, login, logout, decorators
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden
from django.http import JsonResponse
import json
from django.core import serializers
from django.urls import reverse
from .models import (
    User,
    UserProfileInfo,
    Post,
    Comment,
    React,
    FriendRequest,
    FriendList,
    Group,
    GroupMember,
    GroupRequest,
    Block,
    Province,
    Page,
    PersonalInformation,
    Favorites,
    ChatMessage,
    Notification,
)
from django.urls import reverse_lazy
from django.views.generic import (
    View,
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    UpdateView,
)


# Create your views here.
from django.core.exceptions import ObjectDoesNotExist


@login_required(login_url="login")
def get_post_is_login(request):
    user = request.user
    posts = []
    # post - friends
    friend_list = FriendList.objects.filter(user=user)
    if friend_list.count() != 0:
        friends = friend_list.first().friends.all()
        post_list = (
            Post.objects.filter(author__in=friends)
            .exclude(status="only_me")
            .order_by("-created_at")
        )
        posts.extend(post_list)
    # post - group
    group_memberships = GroupMember.objects.filter(member=user)
    for membership in group_memberships:
        group = membership.group
        group_posts = Post.objects.filter(group=group)
        posts.extend(group_posts)
    # post - favorites
    favorites = Favorites.objects.filter(user=user)
    for favorite in favorites:
        if favorite.page:
            page_posts = Post.objects.filter(page=favorite.page)
            posts.extend(page_posts)
        elif favorite.receiver:
            receiver_posts = Post.objects.filter(author=favorite.receiver)
            posts.extend(receiver_posts)
    return posts


def index(request):
    context = {}
    context["MEDIA_URL"] = settings.MEDIA_URL
    if request.user.is_authenticated:
        ## user ##
        user = request.user
        arr_posts = get_post_is_login(request)
        context["arr_posts"] = arr_posts
        user_profile = UserProfileInfo.objects.get(user=request.user)
        context["user_profile"] = user_profile
        ## group ##
        group_memberships = GroupMember.objects.filter(member=request.user)
        groups = [group_membership.group for group_membership in group_memberships]
        context["groups"] = groups
        ## page ##
        page = Page.objects.filter(admin=request.user)
        context["page"] = page
        ## list_friends_posts ##
        friend_list = FriendList.objects.filter(user=user)
        ## list_request_friend
        friend_requests = FriendRequest.objects.filter(
            receiver=request.user, accepted=False
        )
        context["friend_requests"] = friend_requests[:2]
        if friend_list.exists():
            context["has_friend_list"] = True
            friends = friend_list.first().friends.all()
            post_list = (
                Post.objects.filter(author__in=friends)
                .exclude(Q(react__author=user) | Q(comment__author=user))
                .exclude(status="only_me")
                .order_by("-created_at")
            )
            context["post_list"] = post_list
        else:
            context["has_friend_list"] = False
    else:
        pass
    return render(request, "wsite/index.html", context)


####################### AUTH #######################
def register(request):
    registered = False
    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if "profile_pic" in request.FILES:
                profile.profile_pic = request.FILES["profile_pic"]
            profile.save()

            registered = True
            return redirect("login")
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(
        request,
        "auth/signup.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
        },
    )


class LoginView(View):
    def get(self, request):
        return render(request, "auth/login.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is None:
            context = {
                "error_message": "Đăng nhập không thành công. Vui lòng kiểm tra lại tên người dùng và mật khẩu."
            }
            return render(request, "auth/login.html", context)
        login(request, user)
        return redirect("index")


def LogoutView(request):
    logout(request)
    return redirect("index")


from django.db.models import Q


def Profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    try:
        friend_list_data = FriendList.objects.get(user=user)
    except FriendList.DoesNotExist:
        friend_list_data = None

    total_friend_count = friend_list_data.friends.count() if friend_list_data else 0

    user_profile = get_object_or_404(UserProfileInfo, user_id=user_id)

    if request.user.is_authenticated:
        blocked = Block.objects.filter(
            Q(user=request.user, block_user=user)
            | Q(user=user, block_user=request.user)
        )
        if blocked.exists():
            return redirect("403")

        is_friend = FriendList.objects.filter(
            Q(user=request.user, friends=user) | Q(user=user, friends=request.user)
        ).exists()

        is_favorites = Favorites.objects.filter(
            user=request.user, receiver=user
        ).exists()
    else:
        is_friend = False
        is_favorites = False

    try:
        pim = PersonalInformation.objects.get(user=user)
    except PersonalInformation.DoesNotExist:
        pim = None

    if user == request.user:
        post_list = Post.objects.filter(author=user).order_by("-created_at")
    else:
        post_list = (
            Post.objects.filter(author=user)
            .exclude(
                Q(group__isnull=False) | Q(page__isnull=False) | Q(status="only_me")
            )
            .order_by("-created_at")
        )

    friend_lists = FriendList.objects.filter(user=user)
    friends_data = []

    for friend_list in friend_lists:
        friends = friend_list.friends.all()
        for friend in friends:
            if friend.userprofileinfo.profile_pic:
                profile_pic_url = friend.userprofileinfo.profile_pic.url
            else:
                profile_pic_url = None
            friend_data = {
                "id": friend.id,
                "name": friend.username,
                "profile_pic": profile_pic_url,
            }
            friends_data.append(friend_data)

    is_me = user == request.user
    context = {
        "user": user,
        "is_me": is_me,
        "user_profile": user_profile,
        "friends_data": friends_data[:6],
        "pim": pim,
        "post_list": post_list,
        "MEDIA_URL": settings.MEDIA_URL,
        "is_friend": is_friend,
        "is_favorites": is_favorites,
        "total_friend_count": total_friend_count,
    }
    return render(request, "auth/profile_view.html", context)


@decorators.login_required(login_url="login")
def update_bio(request):
    user = request.user
    user_profile, _ = UserProfileInfo.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = UpdateBioForm(request.POST, instance=user_profile)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            return redirect("profile-user", user.id)
    else:
        form = UpdateBioForm(instance=user_profile)
    return redirect("profile-user", user.id)


@login_required
def change_password(request):
    current_password = request.POST.get("current_password")
    new_password1 = request.POST.get("new_password1")
    new_password2 = request.POST.get("new_password2")

    if request.user.check_password(current_password):
        if new_password1 == new_password2:
            request.user.set_password(new_password1)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Your password has been changed successfully.")
        else:
            messages.error(request, "New passwords do not match.")
    else:
        messages.error(request, "Invalid current password.")
    return redirect("profile")


#######################  POST  #######################
@login_required(login_url="login")
def add_post(request):
    if request.method == "POST":
        content = request.POST.get("content")
        status = request.POST.get("status")
        image = request.FILES.get("image")
        post = Post(content=content, author=request.user, status=status, image=image)
        post.save()
        return redirect("index")
    return redirect("index")


@login_required(login_url="login")
def delete_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        if post.author == request.user:
            post.delete()
            referer = request.META.get("HTTP_REFERER")
            if referer:
                return redirect(referer)
            else:
                return redirect("profile-user", request.user.id)
        else:
            return redirect("403")
    except ObjectDoesNotExist:
        raise Http404("Post not found")


class UpdatePostView(UpdateView):
    template_name = "post/edit.html"
    fields = ("content", "image", "status")
    model = Post
    success_url = reverse_lazy("index")

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return redirect("403")
        self.request.POST = self.request.POST.copy()
        self.request.POST["author"] = request.user.id
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["MEDIA_URL"] = settings.MEDIA_URL
        return context


import random


@login_required(login_url="login")
def suggest_users(request):
    all_users = User.objects.all()
    suggested_users = random.sample(list(all_users), k=4)
    return suggested_users


class DetailPostView(DetailView):
    template_name = "post/detail.html"
    context_object_name = "post"
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        comments = Comment.objects.filter(post=post)
        total_react = React.count_react(post.id)
        context["total_react"] = total_react
        context["comments"] = comments
        context["MEDIA_URL"] = settings.MEDIA_URL
        suggested_users = suggest_users(self.request)
        context["suggested_users"] = suggested_users
        if self.request.user.is_authenticated:
            is_react = React.objects.filter(
                post=post, author=self.request.user
            ).exists()
            context["is_react"] = is_react
        return context


#######################  COMMENT  #######################
@decorators.login_required(login_url="login")
def CommentView(request, post_id):
    post = Post.objects.get(id=post_id)
    user = request.user
    if request.method == "POST":
        comment_content = request.POST.get("content")
        comment = Comment.objects.create(
            post=post, author=user, content=comment_content
        )
        comment.save()
        notification = Notification.objects.create(
            user=post.author,
            notification=user.username + " Đã bình luận vào bài viết của bạn.",
            is_seen=False,
        )
        return redirect("detail-post", post.id)


class DeleteCommentView(DeleteView):
    model = Comment
    success_url = reverse_lazy("index")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        post = self.object.post
        user = request.user
        if self.object.author == user or post.author == user:
            self.object.delete()
            return self.get_success_url()
        else:
            return redirect("403")

    def get_success_url(self):
        post = self.object.post
        return reverse("detail-post", kwargs={"pk": post.pk})


@login_required(login_url="login")
def delete_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author == request.user or post.author == request.user:
        comment.delete()
        return redirect("detail-post", post.pk)
    else:
        return HttpResponseForbidden("403 Forbidden")


@login_required(login_url="login")
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        return redirect("403")

    if request.method == "POST":
        content = request.POST.get("content")
        comment.content = content
        comment.save()
        return redirect("detail-post", pk=comment.post.pk)

    return redirect("detail-post", pk=comment.post.pk)


#######################  Like  #######################
class LikeView(View):
    @method_decorator(login_required(login_url=reverse_lazy("login")))
    def post(self, request, post_id):
        post = Post.objects.get(id=post_id)
        user = request.user
        status = request.POST.get("status")
        try:
            react = React.objects.get(post=post, author=user)
            if react.status == status:
                react.delete()
            else:
                react.status = status
                react.save()
        except React.DoesNotExist:
            react = React(post=post, author=user, status=status)
            react.save()
        return redirect("detail-post", post.id)


@login_required(login_url="login")
def react_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    status = request.POST.get("data-action")
    try:
        react = React.objects.get(post=post, author=user)
        if react.status == status:
            react.delete()
        else:
            react.status = status
            react.save()
    except React.DoesNotExist:
        react = React(post=post, author=user, status=status)
        react.save()
    return redirect("detail-post", post.id)


#######################  FRIEND  #######################


@decorators.login_required(login_url="login")
def send_friend_request(request, receiver_id):
    sender = request.user
    receiver = get_object_or_404(User, id=receiver_id)
    friend_request_sent = FriendRequest.objects.filter(
        sender=sender, receiver=receiver
    ).exists()
    are_friends = FriendList.objects.filter(
        Q(user=sender, friends=receiver) | Q(user=receiver, friends=sender)
    ).exists()

    if sender != receiver:
        if friend_request_sent:
            messages.warning(request, "Đã gửi lời mời kết bạn.")
        elif are_friends:
            messages.warning(request, "Hai người đã là bạn bè.")
        else:
            friend_request = FriendRequest(sender=sender, receiver=receiver)
            friend_request.save()
            messages.success(request, "Đã gửi lời mời kết bạn thành công.")
            notification = Notification.objects.create(
                user=receiver,
                notification="Bạn nhận được một lời mời kết bạn từ "
                + sender.username
                + ".",
                is_seen=False,
            )
    else:
        messages.warning(request, "Bạn không thể gửi lời mời kết bạn cho chính mình.")

    return redirect("profile-user", sender.id)


@login_required(login_url="login")
def friend_requests_list(request):
    friend_requests = FriendRequest.objects.filter(
        receiver=request.user, accepted=False
    )
    return render(
        request,
        "auth/friend/friend_requests.html",
        {"friend_requests": friend_requests, "MEDIA_URL": settings.MEDIA_URL},
    )


@login_required(login_url="login")
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(
        FriendRequest, id=request_id, receiver=request.user, accepted=False
    )
    sender = friend_request.sender
    receiver = friend_request.receiver
    friend_request.accepted = True
    friend_request.save()
    sender_friend_list, created = FriendList.objects.get_or_create(user=sender)
    sender_friend_list.friends.add(receiver)
    sender_friend_list.save()
    notification = Notification.objects.create(
        user=sender,
        notification=receiver.username + " Đã chấp nhận yêu cầu kết bạn .",
        is_seen=False,
    )
    receiver_friend_list, created = FriendList.objects.get_or_create(user=receiver)
    receiver_friend_list.friends.add(sender)
    receiver_friend_list.save()
    return redirect("index")


def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    friend_request.delete()
    return redirect("index")


#######################  GROUP  #######################
def is_admin_group(user, group_id):
    group = get_object_or_404(Group, id=group_id)
    return group.admin == user


@login_required(login_url="login")
def create_group(request):
    if request.method == "POST":
        name = request.POST["name"]
        description = request.POST["description"]
        status = request.POST["status"]
        group_pic = request.FILES.get("group_pic")
        group = Group.objects.create(
            name=name,
            description=description,
            status=status,
            admin=request.user,
            group_pic=group_pic,
        )
        GroupMember.objects.create(group=group, member=request.user)
        group_request = GroupRequest.objects.create(
            group=group,
            user=request.user,
            message="Admin",
            approved=True,  # active
        )
        group_request.delete()
        return redirect("group-detail", group.id)
    return render(request, "group/create.html")


@login_required(login_url="login")
def RequestJoinGroup(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    user = request.user
    groupmember = GroupMember.objects.filter(member=user, group=group).first()

    if groupmember is None:
        if group.status == "public":
            GroupMember.objects.create(group=group, member=user)
            return redirect("group-detail", group.pk)
        elif group.status == "private":
            GroupRequest.objects.create(
                group=group,
                user=user,
                message="Xin vào",
                approved=False,
            )
            notification = Notification.objects.create(
                user=user,
                notification="Bạn đã gửi yêu cầu vào nhóm"
                + group.name
                + " vui lòng chờ xét duyệt",
                is_seen=False,
            )
            return redirect("notification")
    return redirect("group-detail", group.pk)


@login_required(login_url="login")
def remove_request_group(request, request_id, group_id):
    group = get_object_or_404(Group, id=group_id)
    user = request.user
    request_group = get_object_or_404(GroupRequest, id=request_id)
    request_group.delete()
    return redirect("group-detail", group.id)


class GroupDetail(DetailView):
    model = Group
    context_object_name = "group"
    template_name = "group/detail.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")  # Chuyển hướng đến trang đăng nhập
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.object
        ## method ##
        group_members = GroupMember.objects.filter(group=group)
        group_requests = GroupRequest.objects.filter(group=group)
        group_post = Post.objects.filter(group=group).order_by("-created_at")
        author_post = Post.objects.filter(
            group=group, author=self.request.user
        ).exists()
        user_authenticated = self.request.user
        author_post = Post.objects.filter(
            group=group, author=user_authenticated
        ).exists()
        context["author_post"] = author_post
        total_member = GroupMember.count_members(group.id)
        total_post = Post.count_posts(group.id)
        check = is_admin_group(self.request.user, group.id)
        is_admin = True if group.admin == self.request.user else False
        users = [group_request.user for group_request in group_requests]
        ## context ##
        context["group_members"] = group_members.all()
        context["group_requests"] = group_requests.all()
        context["check"] = check
        context["is_admin"] = is_admin
        context["users_from_requests"] = users
        context["group_post"] = group_post
        context["author_post"] = author_post
        context["total_member"] = total_member
        context["total_post"] = total_post
        context["MEDIA_URL"] = settings.MEDIA_URL
        return context


@login_required(login_url="login")
def accepted_request_group(request, group_id, user_id):
    user = get_object_or_404(User, id=user_id)
    group = get_object_or_404(Group, id=group_id)
    group_member = GroupMember.objects.filter(group=group, member=user).exists()
    if not group_member:
        group_member = GroupMember.objects.create(group=group, member=user)
        GroupRequest.objects.filter(group=group, user=user).delete()

        return redirect("group-detail", group.pk)
    else:
        return redirect("group-detail", group.pk)


@login_required(login_url="login")
def remove_member(request, user_id, group_id):
    user = request.user
    group = get_object_or_404(Group, id=group_id)
    if group.admin != user:
        return redirect("403")
    member = get_object_or_404(User, id=user_id)
    is_member = GroupMember.objects.filter(group=group, member=member).exists()
    if is_member:
        GroupMember.objects.filter(group=group, member=member).delete()
        return redirect("group-detail", group.pk)


@login_required(login_url="login")
def post_group(request, group_id):
    user = get_object_or_404(User, id=request.user.id)
    group = get_object_or_404(Group, id=group_id)
    group_member = GroupMember.objects.filter(group=group, member=user).exists()
    if group_member:
        if request.method == "POST":
            content = request.POST.get("content", "")
            image = request.FILES.get("image")
            group_post_status = "public"
            post = Post(
                content=content,
                author=request.user,
                image=image,
                status=group_post_status,
                group=group,
            )
            post.save()
            messages.success(request, "Bài viết đã được đăng thành công.")
            return redirect("group-detail", pk=group_id)
        else:
            return redirect("group-detail", pk=group_id)
    else:
        messages.error(request, "Bạn không phải là thành viên của nhóm.")
        return redirect("group-detail", pk=group_id)


@login_required(login_url="login")
def delete_post_group(request, group_id, post_id):
    user = get_object_or_404(User, id=request.user.id)
    group = get_object_or_404(Group, id=group_id)
    group_member = GroupMember.objects.filter(group=group, member=user).exists()
    author_post = Post.objects.filter(group=group, author=user).exists()
    post = Post.objects.get(id=post_id, group=group)

    if group_member and (author_post or user.is_superuser):
        if post:
            post.delete()
    else:
        return redirect("403")
    return redirect("group-detail", group.id)


#######################  OTHER  #######################


def SearchView(request):
    context = {}
    context["MEDIA_URL"] = settings.MEDIA_URL
    keyword = request.GET["keyword"]
    if request.user.is_authenticated:
        context["is_authenticated"] = True
        users = User.objects.filter(username__icontains=keyword)
        blocked_users = Block.objects.filter(
            block_user__in=users, user=request.user
        ).values_list("block_user", flat=True)
        groups = Group.objects.filter(name__icontains=keyword)
        pages = Page.objects.filter(name__icontains=keyword)
        context["users"] = users.exclude(pk__in=blocked_users)
        context["groups"] = groups
        context["pages"] = pages

    else:
        all_user = User.objects.filter(username__icontains=keyword)
        all_group = Group.objects.filter(name__icontains=keyword)
        all_page = Page.objects.filter(name__icontains=keyword)
        context["all_user"] = all_user
        context["all_group"] = all_group
        context["all_page"] = all_page
    return render(request, "search/index.html", context)


#######################  BLOCK #######################
@login_required(login_url="login")
def block_user(request, blocked_user_id):
    block_user = get_object_or_404(User, id=blocked_user_id)
    user = request.user
    if user.friends.filter(user=block_user).exists():
        user_friends = FriendList.objects.get(user=user)
        blocked_friend = FriendList.objects.get(user=block_user)
        user_friends.friends.remove(block_user)
        blocked_friend.friends.remove(user)
    # xu ly
    block = Block(user=user, block_user=block_user)
    block.save()
    return redirect("list-block")


@decorators.login_required(login_url="login")
def list_block(request):
    user = request.user
    list_block = Block.objects.filter(user=user).select_related("user").all()
    context = {
        "MEDIA_URL": settings.MEDIA_URL,
        "list_block": list_block,
    }
    return render(request, "auth/block/index.html", context)


@login_required(login_url="login")
def un_block(request, blocked_id):
    blocked = Block.objects.get(id=blocked_id)
    blocked.delete()
    return redirect("list-block")


@login_required(login_url="login")
def unblock_user(request, blocked_user_id):
    user = request.user
    blocked_user = get_object_or_404(User, id=blocked_user_id)

    # Kiểm tra quyền truy cập của người dùng hiện tại
    if Block.objects.filter(user=user, block_user=blocked_user).exists():
        block = get_object_or_404(Block, user=user, block_user=blocked_user)
        block.delete()
        return redirect("list-block")
    else:
        return redirect("403")


#######################  Province  #######################
def province_view(request):
    province = Province.objects.all()
    context = {
        "province": province,
    }
    return render(request, "province/index.html", context)


class ProvinceCreateView(CreateView):
    model = Province
    fields = ["slug", "name"]
    template_name = "province/create.html"
    success_url = reverse_lazy("province")


class ProvinceUpdateView(UpdateView):
    model = Province
    fields = ["slug", "name"]
    context_object_name = "province"
    template_name = "province/edit.html"
    success_url = reverse_lazy("province")


class ProvinceDeleteView(DeleteView):
    model = Province
    success_url = reverse_lazy("province")


#######################  Page  #######################
class PageCreateView(CreateView):
    model = Page
    fields = [
        "name",
        "category",
        "description",
        "province",
        "page_profile_pic",
        "admin",
    ]
    template_name = "page/create.html"
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        admin = self.request.user
        form.instance.admin = admin
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        provinces = Province.objects.all()
        context["provinces"] = provinces
        return context


@login_required(login_url="login")
def create_page(request):
    province = Province.objects.all()
    context = {"provinces": province}
    user = request.user
    if request.method == "POST":
        name = request.POST["name"]
        category = request.POST["category"]
        description = request.POST["description"]
        province_id = request.POST["province"]
        province = Province.objects.get(id=province_id)
        page_profile_pic = request.FILES.get("page_profile_pic")
        page = Page(
            name=name,
            category=category,
            description=description,
            province=province,
            admin=user,
            page_profile_pic=page_profile_pic,
        )
        page.save()
        favorites = Favorites.objects.create(user=user, page=page)
        return redirect("page", page.id)
    return render(request, "page/create.html", context)


class DeletePageView(DeleteView):
    model = Page
    success_url = reverse_lazy("index")


class PageDetailView(DetailView):
    model = Page
    context_object_name = "page"
    template_name = "page/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.get_object()
        posts = Post.objects.filter(page=page).order_by("-created_at")
        total_post = Post.objects.filter(page=page).count()
        total_favorites_page = Favorites.objects.filter(page=page).count()
        context["total_favorites_page"] = total_favorites_page
        context["total_post"] = total_post
        context["posts"] = posts
        context["MEDIA_URL"] = settings.MEDIA_URL

        if self.request.user.is_authenticated:
            user = self.request.user
            is_favorited = Favorites.objects.filter(user=user, page=page).exists()
            context["is_favorited"] = is_favorited
            is_admin = Page.objects.filter(admin=user).exists()
            context["is_admin"] = is_admin
        return context


@login_required(login_url="login")
def editPage(request, page_id):
    user = request.user
    page = get_object_or_404(Page, id=page_id)
    if page.admin != user:
        return redirect("403")
    provinces = Province.objects.all()
    context = {
        "page": page,
        "provinces": provinces,
    }
    return render(request, "page/update.html", context)


@login_required(login_url="login")
def edit_group(request, group_id):
    user = request.user
    group = get_object_or_404(Group, id=group_id)
    if group.admin != user:
        return redirect("403")
    context = {
        "group": group,
    }
    return render(request, "group/edit.html", context)


@login_required(login_url="login")
def update_group(request, group_id):
    user = request.user
    group = get_object_or_404(Group, id=group_id)
    if group.admin != user:
        return redirect("403")
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        status = request.POST.get("status")
        group.name = name
        group.description = description
        group.status = status
        group.save()
    return redirect("group-detail", group.id)


@login_required(login_url="login")
def update_page(request, page_id):
    user = request.user
    page = get_object_or_404(Page, id=page_id)
    if page.admin != user:
        return redirect("403")
    if request.method == "POST":
        name = request.POST.get("name")
        category = request.POST.get("category")
        description = request.POST.get("description")
        province_id = request.POST["province"]
        province = Province.objects.get(id=province_id)
        page.name = name
        page.category = category
        page.description = description
        page.province = province
        page.admin = user
        page.save()
    return redirect("page", page.id)


@login_required(login_url="login")
def page_create_post(request, page_id):
    user = get_object_or_404(User, id=request.user.id)
    page = get_object_or_404(Page, id=page_id)
    if request.method == "POST":
        content = request.POST.get("content", "")
        image = request.FILES.get("image")
        page_status = "public"
        post = Post(
            content=content,
            author=request.user,
            image=image,
            status=page_status,
            page=page,
        )
        post.save()
        return redirect("page", page.pk)


@login_required(login_url="login")
def update_pim(request):
    user = request.user
    if request.method == "POST":
        pim = PersonalInformation.objects.get_or_create(user=user)[0]
        home_town_id = request.POST.get("home_town")
        if home_town_id:
            home_town = Province.objects.get(id=home_town_id)
            pim.home_town = home_town
        residence_id = request.POST.get("residence")
        if residence_id:
            residence = Province.objects.get(id=residence_id)
            pim.residence = residence
        sex = request.POST.get("sex")
        if sex:
            pim.sex = sex
        relationship = request.POST.get("relationship")
        if relationship:
            pim.relationship = relationship
        degree = request.POST.get("degree")
        if degree:
            pim.degree = degree
        workplace_id = request.POST.get("workplace")
        if workplace_id:
            workplace = Page.objects.get(id=workplace_id)
            pim.workplace = workplace
        pim.save()
    return redirect("profile-user", user.id)


@login_required(login_url="login")
def setting_profile(request):
    provinces = Province.objects.all()
    pages = Page.objects.all()
    context = {
        "provinces": provinces,
        "pages": pages,
    }
    return render(request, "auth/setting_profile.html", context)


def chatPage(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login")
    context = {}
    return render(request, "chat.html")


def View403(request):
    return render(request, "wsite/403.html")


@login_required(login_url="login")
def favorites_page(request, page_id):
    user = request.user
    page = get_object_or_404(Page, id=page_id)
    is_favorited = Favorites.objects.filter(user=user, page=page).exists()
    if not is_favorited:
        favorite_page = Favorites(user=user, page=page)
        favorite_page.save()
    return redirect("page", page.pk)


@login_required(login_url="login")
def un_favorites_page(request, page_id):
    user = request.user
    page = get_object_or_404(Page, id=page_id)
    is_favorited = Favorites.objects.filter(user=user, page=page).exists()
    if is_favorited:
        Favorites.objects.filter(user=user, page=page).delete()
    return redirect("page", page.pk)


@login_required(login_url="login")
def favorites_user(request, user_id):
    user = request.user
    receiver = get_object_or_404(User, id=user_id)
    is_favorited = Favorites.objects.filter(user=user, receiver=receiver).exists()
    if not is_favorited:
        favorite_user = Favorites(user=user, receiver=receiver)
        favorite_user.save()
    return redirect("profile-user", receiver.id)


@login_required(login_url="login")
def un_favorites_user(request, user_id):
    user = request.user
    receiver = get_object_or_404(User, id=user_id)
    is_favorited = Favorites.objects.filter(user=user, receiver=receiver).exists()
    if is_favorited:
        Favorites.objects.filter(user=user, receiver=receiver).delete()
    return redirect("profile-user", receiver.id)


@login_required(login_url="login")
def un_friend(request, user_id):
    user = request.user
    friend = get_object_or_404(User, id=user_id)

    try:
        user_friend_list = FriendList.objects.get(user=user)
        friend_friend_list = FriendList.objects.get(user=friend)
        user_friend_list.remove_friend(friend)
        friend_friend_list.remove_friend(user)
        return redirect("profile-user", friend.id)
    except FriendList.DoesNotExist:
        raise Http404(
            "Không tìm thấy danh sách bạn bè hoặc bạn không có quyền xóa mối quan hệ bạn bè."
        )


@login_required(login_url="login")
def react_like(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    is_react = React.objects.filter(post=post, author=user).exists()
    status = "like"
    if not is_react:
        React.objects.create(post=post, author=user, status=status)
        notification = Notification.objects.create(
            user=post.author,
            notification=user.username + " Đã " + status + " bài viết của bạn",
            is_seen=False,
        )
    else:
        React.objects.filter(post=post, author=user, status=status).delete()
    return redirect("detail-post", post.pk)


@login_required(login_url="login")
def react_favorites(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    is_react = React.objects.filter(post=post, author=user).exists()
    status = "favourite"
    if not is_react:
        React.objects.create(post=post, author=user, status=status)
        notification = Notification.objects.create(
            user=post.author,
            notification=user.username + " Đã " + status + " bài viết của bạn",
            is_seen=False,
        )
    else:
        React.objects.filter(post=post, author=user, status=status).delete()
    return redirect("detail-post", post.pk)


@login_required(login_url="login")
def react_sad(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    is_react = React.objects.filter(post=post, author=user).exists()
    status = "sad"
    if not is_react:
        React.objects.create(post=post, author=user, status=status)
        notification = Notification.objects.create(
            user=post.author,
            notification=user.username + " Đã " + status + " bài viết của bạn",
            is_seen=False,
        )
    else:
        React.objects.filter(post=post, author=user, status=status).delete()
    return redirect("detail-post", post.pk)


@login_required(login_url="login")
def react_angry(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    is_react = React.objects.filter(post=post, author=user).exists()
    status = "angry"
    if not is_react:
        React.objects.create(post=post, author=user, status=status)
        notification = Notification.objects.create(
            user=post.author,
            notification=user.username + " Đã " + status + " bài viết của bạn",
            is_seen=False,
        )
    else:
        React.objects.filter(post=post, author=user, status=status).delete()
    return redirect("detail-post", post.pk)


@login_required(login_url="login")
def un_react(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    is_react = React.objects.filter(post=post, author=user).exists()
    if is_react:
        React.objects.filter(post=post, author=user).delete()
    return redirect("detail-post", post.pk)


@login_required
def update_profile_pic(request):
    user = request.user
    profile = UserProfileInfo.objects.get(user=user)
    if request.method == "POST" and "profile_pic" in request.FILES:
        profile.profile_pic = request.FILES["profile_pic"]
        profile.save()
        return redirect("profile-user", user.id)
    return redirect("profile-user", user.id)


@login_required(login_url="login")
def add_reply(request, comment_id):
    if request.method == "POST":
        parent_comment = get_object_or_404(Comment, id=comment_id)
        post = parent_comment.post
        content = request.POST.get("content")
        author = request.user
        reply = Comment(
            post=post, author=author, content=content, parent_comment=parent_comment
        )
        reply.save()

        return redirect("detail-post", pk=post.pk)
    else:
        return redirect("detail-post", pk=post.pk)


@login_required(login_url="login")
def chat(request):
    user = request.user
    context = {}
    context["MEDIA_URL"] = settings.MEDIA_URL
    if FriendList.objects.filter(user=user).exists():
        friend_list = FriendList.objects.get(user=user)
        friends = friend_list.get_all_friends()
        context["friends"] = friends
    return render(request, "chat/index.html", context)


@login_required(login_url="login")
def chat_detail(request, user_id):
    # form
    user = request.user
    receiver = get_object_or_404(User, id=user_id)
    # data
    friend_list = FriendList.objects.get(user=user)
    friends = friend_list.get_all_friends()

    # chat
    chat_messages = ChatMessage.get_chat_messages(user, receiver)
    rec_chats = ChatMessage.objects.filter(msg_sender=receiver, msg_receiver=user)
    forms = ChatMessageForm()
    if request.method == "POST":
        forms = ChatMessageForm(request.POST)
        if forms.is_valid():
            chat_message = forms.save(commit=False)
            chat_message.msg_sender = user
            chat_message.msg_receiver = receiver
            chat_message.save()
            return redirect("detail-chat", receiver.id)
    context = {
        "MEDIA_URL": settings.MEDIA_URL,
        "friends": friends,
        "forms": forms,
        "user": user,
        "receiver": receiver,
        "chat_messages": chat_messages,
        "num": rec_chats.count(),
    }
    return render(request, "chat/detail.html", context)


@login_required(login_url="login")
def sentMessage(request, user_id):
    user = request.user
    receiver = get_object_or_404(User, id=user_id)
    new_chat = request.POST.get("msg")
    img = request.FILES.get("img")
    new_chat_message = ChatMessage.objects.create(
        body=new_chat, msg_sender=user, msg_receiver=receiver
    )
    if img is not None:
        new_chat_message.img = img
        new_chat_message.save()
    response_data = {
        "body": new_chat_message.body,
        "img": new_chat_message.img.name if new_chat_message.img else None,
    }
    return JsonResponse(response_data, safe=False)


@login_required(login_url="login")
def receivedMessages(request, user_id):
    user = request.user
    receiver = get_object_or_404(User, id=user_id)
    arrChat = []
    chats = ChatMessage.objects.filter(msg_sender=receiver, msg_receiver=user).values(
        "body", "img"
    )
    for chat in chats:
        chat_data = {
            "body": chat["body"],
            "img": chat["img"] if chat["img"] else None,
        }
        arrChat.append(chat_data)
    return JsonResponse(arrChat, safe=False)


@login_required(login_url="login")
def notification(request):
    return render(request, "notification/index.html")


@login_required(login_url="login")
def get_notification(request):
    user = request.user
    notifications = Notification.objects.filter(user=user, is_seen=False).order_by(
        "-created_at"
    )
    arr_notification = [n.notification for n in notifications]
    return JsonResponse(arr_notification, safe=False)


@login_required(login_url="login")
def list_friend(request):
    user = request.user
    friends = FriendList.get_all_friends(user)
    context = {"user": user, "friends": friends}
    return render(request, "auth/friend/list_friend.html", context)


def setting_view(request):
    current_user = request.user if request.user.is_authenticated else None
    context = {
        "MEDIA_URL": settings.MEDIA_URL,
        "user": current_user,
    }
    return render(request, "wsite/setting.html", context)


@login_required(login_url="login")
def out_group(request, group_id):
    user = request.user
    group = get_object_or_404(Group, id=group_id)
    if GroupMember.objects.filter(group=group, member=user).exists():
        if user == group.admin:
            notifications = Notification.objects.create(
                user=user,
                notification="Bạn không thể  rời nhóm vì bạn là admin hãy ủy quyền trước khi rời nhóm!",
                is_seen=False,
            )
            return redirect("notification")
        else:
            GroupMember.objects.filter(group=group, member=user).delete()
            return redirect("index")
