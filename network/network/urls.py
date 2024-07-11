from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("newpost", views.newpost, name="newpost"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("following", views.following, name="following"),
    path("editpost/<int:post_id>", views.edit, name="edit"),
    path("like_unlike/<int:post_id>", views.like_unlikeposts, name="like_unlike"),
    path("follow/<str:username>", views.follow, name="follow"),
]
