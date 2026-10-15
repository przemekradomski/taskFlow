from django.urls import path, re_path

from taskFlow import api, views

urlpatterns = [
    path("api/me/", api.me, name="api_me"),
    path("api/auth/login/", api.login_view, name="api_login"),
    path("api/auth/first-login/", api.first_login_view, name="api_first_login"),
    path("api/auth/logout/", api.logout_view, name="api_logout"),
    path("api/tasks/", api.tasks, name="api_tasks"),
    path("api/tasks/<int:issue_id>/", api.task_detail, name="api_task_detail"),
    path("api/admin/users/", api.admin_users, name="api_admin_users"),
    path(
        "api/admin/users/<int:user_id>/",
        api.admin_user_delete,
        name="api_admin_user_delete",
    ),
    path("api/profile/", api.profile, name="api_profile"),
    re_path(r"^(?!(?:admin|api|media|static)(?:/|$)).*$", views.spa, name="spa"),
]
