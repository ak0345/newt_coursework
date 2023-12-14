from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from datetime import datetime
from django.utils import timezone


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
    gravatar_url = models.URLField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False)

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

def validate_future_date(value):
    if value < timezone.now():
        raise ValidationError("The date cannot be in the past.")


class Task(models.Model):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

    STATUS_CHOICES = [
        (NOT_STARTED, "Not Started"),
        (IN_PROGRESS, "In Progress"),
        (COMPLETED, "Completed"),
    ]

    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

    PRIORITY_CHOICES = [
        (HIGH, "High"),
        (MEDIUM, "Medium"),
        (LOW, "Low"),
    ]
    task_heading = models.CharField(max_length=50, blank=False)
    task_description = models.CharField(max_length=160, null=True, blank=True)
    team_assigned = models.ForeignKey(
        "Team",
        on_delete=models.CASCADE,
        related_name="team_assigned_tasks",
    )
    task_owner = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="tasks_owned",
    )
    user_assigned = models.ManyToManyField(
        "User",
        blank=True,
        related_name="assigned_tasks",
    )
    creation_date = models.DateTimeField(auto_now_add=True, blank=False)
    last_modified = models.DateTimeField(auto_now=True, blank=False)
    deadline_date = models.DateTimeField(null=True, blank=True, validators=[validate_future_date])
    task_complete = models.BooleanField(default=False)
    completion_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=NOT_STARTED
    )

    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=LOW)

    class Meta:
        ordering = ["task_heading"]

    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

    STATUS_CHOICES = [
        (NOT_STARTED, "Not Started"),
        (IN_PROGRESS, "In Progress"),
        (COMPLETED, "Completed"),
    ]

    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

    PRIORITY_CHOICES = [
        (HIGH, "High"),
        (MEDIUM, "Medium"),
        (LOW, "Low"),
    ]

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
    creation_date = models.DateTimeField(auto_now_add=True)
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

    def __str__(self):
        return self.team_name


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, blank=False)
    Commentor = models.ForeignKey(User, on_delete=models.CASCADE, null=False, default = 1)  # New field for the commenter


    def comment_description(self):
        return f"Comment on {self.task.task_heading}"

      
class Invitation(models.Model):
    user_requesting_to_join = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="user_requesting_to_join",
    )
    user_creating_invitation = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="user_creating_invitation",
    )
    team_to_join = models.ForeignKey(
        "Team",
        on_delete=models.CASCADE,
    )
