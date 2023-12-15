# Generated by Django 4.2.6 on 2023-12-15 14:59

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import tasks.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        max_length=30,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Username must consist of @ followed by at least three alphanumericals",
                                regex="^@\\w{3,}$",
                            )
                        ],
                    ),
                ),
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(max_length=50)),
                (
                    "gravatar_url",
                    models.URLField(blank=True, max_length=255, null=True),
                ),
                ("points", models.IntegerField(default=0)),
                ("email", models.EmailField(max_length=254, unique=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={"ordering": ["last_name", "first_name"],},
            managers=[("objects", django.contrib.auth.models.UserManager()),],
        ),
        migrations.CreateModel(
            name="Team",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("team_name", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("creation_date", models.DateTimeField(auto_now_add=True)),
                ("last_modified", models.DateTimeField(auto_now=True)),
                (
                    "unique_identifier",
                    models.CharField(
                        max_length=50,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Unqiue identifer must consist of # followed by at least three alphanumericals",
                                regex="^#\\w{3,}$",
                            )
                        ],
                    ),
                ),
                (
                    "team_owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="teams_owned",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "users_in_team",
                    models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("task_heading", models.CharField(max_length=50)),
                (
                    "task_description",
                    models.CharField(blank=True, max_length=160, null=True),
                ),
                ("creation_date", models.DateTimeField(auto_now_add=True)),
                ("last_modified", models.DateTimeField(auto_now=True)),
                (
                    "deadline_date",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        validators=[tasks.models.validate_future_date],
                    ),
                ),
                ("task_complete", models.BooleanField(default=False)),
                ("completion_time", models.DateTimeField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Not Started", "Not Started"),
                            ("In Progress", "In Progress"),
                            ("Completed", "Completed"),
                        ],
                        default="Not Started",
                        max_length=20,
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("High", "High"),
                            ("Medium", "Medium"),
                            ("Low", "Low"),
                        ],
                        default="Low",
                        max_length=10,
                    ),
                ),
                (
                    "task_owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks_owned",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "team_assigned",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="team_assigned_tasks",
                        to="tasks.team",
                    ),
                ),
                (
                    "user_assigned",
                    models.ManyToManyField(
                        blank=True,
                        related_name="assigned_tasks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["task_heading"],},
        ),
        migrations.CreateModel(
            name="Invitation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "team_to_join",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="tasks.team"
                    ),
                ),
                (
                    "user_creating_invitation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_creating_invitation",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user_requesting_to_join",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_requesting_to_join",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.TextField()),
                ("created_at", models.DateTimeField(auto_now=True)),
                (
                    "Commentor",
                    models.ForeignKey(
                        default=1,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="tasks.task"
                    ),
                ),
            ],
        ),
    ]
