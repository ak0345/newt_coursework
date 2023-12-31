from django.contrib import admin
from .models import User, Task, Team, Comment, Invitation

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ("username",)
    list_display = [
        "username",
        "first_name",
        "last_name",
        "email",
        "points",
        "owned_teams",
        "owned_task_ids",
        "team_memberships",
        "is_active",
        "is_staff",
    ]

    def owned_teams(self, obj):
        team_ids = Team.objects.filter(team_owner=obj).values_list('unique_identifier', flat=True)
        teams = []
        for team_id in team_ids:
            teams.append(team_id)
        return teams if teams else "None"



    def owned_task_ids(self, obj):
        task_ids = Task.objects.filter(task_owner=obj).values_list('id', flat=True)
        tasks = []
        for task_id in task_ids:
            tasks.append(task_id)
        return tasks if tasks else "None"
    
    def team_memberships(self, obj):
        team_ids = Team.objects.filter(users_in_team=obj).values_list('unique_identifier', flat=True)
        teams = []
        for team_id in team_ids:
            teams.append(team_id)
        return teams if teams else "None"


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    search_fields = ("unique_identifier", "users_in_team__username", "team_owner__username","team_name")
    list_display = [
        "unique_identifier",
        "team_name",
        "description",
        "points",
        "team_owner",
        "users_in_team_list",
        "owned_tasks",
        "creation_date",
        "last_modified",
    ]

    def users_in_team_list(self, obj):
        usernames_out = []
        for username_obj in obj.users_in_team.all():
            usernames_out.append(username_obj.username)
        return usernames_out if usernames_out else "None"

    def owned_tasks(self, obj):
        task_ids = Task.objects.filter(team_assigned=obj).values_list('id', flat=True)
        tasks = []
        for task_id in task_ids:
            tasks.append(task_id)
        return tasks if tasks else "None"
    
    def points(self, obj):
        total_points = 0
        total_points += obj.team_owner.points
        for user in obj.users_in_team.all():
            total_points += user.points
        return total_points


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    search_fields = ("id", "task_owner__username", "user_assigned__username", "task_heading", )
    list_display = [
        "id",
        "task_heading",
        "creation_date",
        "last_modified",
        "task_owner",
        "user_assigned_to_task",
        "team_assigned",
        "priority",
        "status",
    ]

    def user_assigned_to_task(self, obj):
        usernames_out = []
        for username_obj in obj.user_assigned.all():
            usernames_out.append(username_obj.username)
        return usernames_out if usernames_out else "None"
    
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    search_fields = ("Commentor__username", "task__task_heading")
    list_display = [
        "id",
        "task",
        "text",
        "Commentor",
    ]

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    search_fields = ("team_to_join__unique_identifier", )
    list_display = [
        "id",
        "team_to_join",
        "user_requesting_to_join",
        "user_creating_invitation",
    ]