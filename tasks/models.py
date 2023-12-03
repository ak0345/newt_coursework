from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from datetime import datetime


class User(AbstractUser):
    """Model used for user authentication, and team member related information."""

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^@\w{3,}$",
                message="Username must consist of @ followed by at least three alphanumericals",
            )
        ],
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    owned_tasks = models.ManyToManyField("Task", blank=True, related_name="task_owners")
    owned_teams = models.ManyToManyField("Team", blank=True, related_name="team_owners")

    class Meta:
        """Model options."""

        ordering = ["last_name", "first_name"]

    def full_name(self):
        """Return a string containing the user's full name."""

        return f"{self.first_name} {self.last_name}"

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""

        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default="mp")
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""

        return self.gravatar(size=60)


class Task(models.Model):
    task_heading = models.CharField(max_length=50, blank=False)
    task_description = models.CharField(max_length=160, null=True, blank=True)
    team_assigned = models.ForeignKey(
        "Team",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_assigned",
    )
    task_owner = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="tasks_owned", default=0
    )
    user_assigned = models.ManyToManyField(
        "User",
        blank=True,
        related_name="assigned_users",
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    deadline_date = models.DateTimeField(null=True, blank=True)
    task_complete = models.BooleanField(default=False)

    # allow one task to have sub-tasks without those sub-tasks necessarily having the original task as a parent.
    sub_tasks = models.ManyToManyField(
        "self", blank=True, symmetrical=False, related_name="subtasks"
    )

    class Meta:
        """Model options."""

        ordering = ["task_heading"]

    def __str__(self):
        return self.task_heading


class Team(models.Model):
    team_name = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=False)
    team_owner = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="teams_owned",
        default="default_owner",
    )
    users_in_team = models.ManyToManyField(
        "User",
        blank=True
        # validators = [check_users_team] - this may need to be updated / a new one made
    )
    creation_date = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now=True)
    unique_identifier = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^#\w{3,}$",
                message="Unqiue identifer must consist of # followed by at least three alphanumericals",
            )
        ],
    )


class Invitation(models.Model):
    user_requesting_to_join = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
    )
    team_to_join = models.ForeignKey(
        "Team",
        on_delete=models.CASCADE,
    )
