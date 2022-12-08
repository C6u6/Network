
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path("profile/<int:profile_id>", views.profile, name="profile"),
    path("content_following", views.content_following, name="content_following"),
    path("update_likes/<int:post_id>", views.likes, name="update_likes"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path("alter_follow_state/<int:person_id>", views.alter_follow_state, name="alter_follow_state"),
]
