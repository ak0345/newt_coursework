from django.contrib import admin
from .models import User, Task, Team, Invitation

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "first_name",
        "last_name",
        "email",
        "is_active",
        "is_staff",
    ]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = [
        "unique_identifier",
        "team_name",
        "description",
        "team_owner",
        "creation_date",
        "last_modified",
    ]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "task_heading",
        "creation_date",
        "last_modified",
        "task_owner",
        "task_complete",
    ]


@admin.register(Invitation)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "team_to_join",
        "user_requesting_to_join",
    ]
