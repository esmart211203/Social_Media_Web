from . import views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.LoginView.as_view(), name="login"),
    path("logout", views.LogoutView, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<int:user_id>", views.Profile, name="profile-user"),
    path("profile/update/bio", views.update_bio, name="update_bio"),
    path("profile/setting", views.setting_profile, name="s&f"),
    path("change/password", views.change_password, name="change-password"),
    path("add_post", views.add_post, name="add-post"),
    path("delete-post/<int:post_id>", views.delete_post, name="delete-post"),
    path("update/post/<int:pk>", views.UpdatePostView.as_view(), name="update-post"),
    path("detail/post/<int:pk>", views.DetailPostView.as_view(), name="detail-post"),
    path(
        "page-create-post/<int:page_id>",
        views.page_create_post,
        name="page-create-post",
    ),
    path("react-post/<int:post_id>/like", views.react_like, name="react-like"),
    path(
        "react-post/<int:post_id>/favorites",
        views.react_favorites,
        name="react-favorites",
    ),
    path("react-post/<int:post_id>/sad", views.react_sad, name="react-sad"),
    path("react-post/<int:post_id>/angry", views.react_angry, name="react-angry"),
    path("comment/<int:post_id>", views.CommentView, name="comment"),
    path("reppy/comment/<int:comment_id>", views.add_reply, name="repply-comment"),
    path(
        "delete/comment/<int:pk>",
        views.DeleteCommentView.as_view(),
        name="delete-comment",
    ),
    path(
        "delete/comment/<int:post_id>/<int:comment_id>",
        views.delete_comment,
        name="del_cmt",
    ),
    path("update/comment/<int:comment_id>", views.edit_comment, name="edit-comment"),
    path("like/<int:post_id>/", views.LikeView.as_view(), name="like"),
    path("react/<int:post_id>", views.react_post, name="react"),
    path(
        "send_friend_request/<int:receiver_id>",
        views.send_friend_request,
        name="send_friend_request",
    ),
    path("friend-requests/", views.friend_requests_list, name="friend-requests"),
    path(
        "friend-requests/<int:request_id>/accept/",
        views.accept_friend_request,
        name="accept-friend-request",
    ),
    path(
        "decline-friend-request/<int:request_id>",
        views.decline_friend_request,
        name="decline-request",
    ),
    path("create-group", views.create_group, name="create-group"),
    path("request-join-group/<int:group_id>", views.RequestJoinGroup, name="r-j-group"),
    path("group-detail/<int:pk>", views.GroupDetail.as_view(), name="group-detail"),
    path(
        "accepted-request-group/<int:group_id>/<int:user_id>/",
        views.accepted_request_group,
        name="accepted-r-g",
    ),
    path(
        "remove/request/<int:request_id>/<int:group_id>",
        views.remove_request_group,
        name="remove_request",
    ),
    path(
        "remove-member/<int:group_id>/<int:user_id>",
        views.remove_member,
        name="remove_member",
    ),
    path("post-group/<int:group_id>", views.post_group, name="post-group"),
    path(
        "delete-post-group/<int:group_id>/<int:post_id>",
        views.delete_post_group,
        name="del-post-group",
    ),
    path("search", views.SearchView, name="search"),
    path("list-block", views.list_block, name="list-block"),
    path("block-user/<int:blocked_user_id>", views.block_user, name="block-user"),
    path("un-block- user/<int:blocked_user_id>", views.unblock_user, name="un-block"),
    path("province", views.province_view, name="province"),
    path("province/create", views.ProvinceCreateView.as_view(), name="province-create"),
    path(
        "province/<int:pk>/delete",
        views.ProvinceDeleteView.as_view(),
        name="province-delete",
    ),
    path(
        "province/<int:pk>/update",
        views.ProvinceUpdateView.as_view(),
        name="province-update",
    ),
    path("page/<int:pk>", views.PageDetailView.as_view(), name="page"),
    path("create-page", views.create_page, name="create-page"),
    path("delete/<int:pk>", views.DeletePageView.as_view(), name="delete-page"),
    path("favorites/page/<int:page_id>", views.favorites_page, name="favorites-page"),
    path(
        "Unfavorites/page/<int:page_id>",
        views.un_favorites_page,
        name="un-favorites-page",
    ),
    path("favorites/user/<int:user_id>", views.favorites_user, name="favorites-user"),
    path(
        "Unfavorites/user/<int:user_id>",
        views.un_favorites_user,
        name="un-favorites-user",
    ),
    path("un-react/<int:post_id>", views.un_react, name="un_react"),
    path("un-friend/<int:user_id>", views.un_friend, name="un-friend"),
    path("update-pim", views.update_pim, name="pim"),
    path("update-avatar", views.update_profile_pic, name="update-avatar"),
    path("chat111", views.chatPage),
    path("notification", views.notification, name="notification"),
    path("403", views.View403, name="403"),
    path("chat", views.chat, name="chat"),
    path("detail/chat/<int:user_id>", views.chat_detail, name="detail-chat"),
    path("sent_msg/<int:user_id>", views.sentMessage, name="sent_msg"),
    path("rec_msg/<int:user_id>", views.receivedMessages, name="rec_msg"),
    path("get-notification/", views.get_notification, name="get_notification"),
    path("list_friend", views.list_friend, name="list_friend"),
    path("edit/page/<int:page_id>", views.editPage, name="edit_page"),
    path("edit/group/<int:group_id>", views.edit_group, name="edit_group"),
    path("update/page/<int:page_id>", views.update_page, name="update_page"),
    path("update/group/<int:group_id>", views.update_group, name="update_group"),
    path("out/group/<int:group_id>", views.out_group, name="group_id"),
    path("check", views.get_post_is_login),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)