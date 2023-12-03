"""
URL configuration for task_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import re_path
from tasks import views
from tasks.views import create_team
from tasks.views import team_search

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("log_in/", views.LogInView.as_view(), name="log_in"),
    path("log_out/", views.log_out, name="log_out"),
    path("password/", views.PasswordView.as_view(), name="password"),
    path("profile/", views.ProfileUpdateView.as_view(), name="profile"),
    path("sign_up/", views.SignUpView.as_view(), name="sign_up"),
    path("create_team/", create_team, name="create_team"),
    path("create_task/", views.create_task, name="create_task"),
    path("team_management/", team_search, name="team_management"),
    path("team/<int:team_id>", views.show_team, name="show_team"),
    path("task/<int:task_id>/", views.show_task_details, name="show_task"),
    path("delete_task/<int:task_id>/", views.delete_task, name="delete_task"),
    path("high-priority-tasks/", views.high_priority_tasks, name="high_priority_tasks"),
    path(
        "medium-priority-tasks/",
        views.medium_priority_tasks,
        name="medium_priority_tasks",
    ),
    path("low-priority-tasks/", views.low_priority_tasks, name="low_priority_tasks"),
    path("add_comment/<int:task_id>/", views.add_comment, name="add_comment"),
    path("add_comment/<int:task_id>/", views.add_comment, name="add_comment"),
    path("add_comment/<int:task_id>/", views.add_comment, name="add_comment"),
    path("edit_task/<int:task_id>/", views.edit_task, name="edit_task"),
    path("edit_team/<int:team_id>/", views.edit_team, name="edit_team"),
    path("team/<int:team_id>/delete/", views.team_delete, name="team_delete"),
    path(
        "tasks/<int:task_id>/update_status/",
        views.update_task_status,
        name="update_task_status",
    ),
    path("team_search/", views.lookup_team, name="lookup-team"),
    path("everything_search/", views.lookup_everything, name="lookup-everything"),
    path("leave_team/<int:team_id>/", views.leave_team, name="leave_team"),
]
