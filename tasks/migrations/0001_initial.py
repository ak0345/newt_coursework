from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


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
            ],
            options={
                "ordering": ["last_name", "first_name"],
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
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
                ("deadline_date", models.DateTimeField(blank=True, null=True)),
                ("task_complete", models.BooleanField(default=False)),
                (
                    "sub_tasks",
                    models.ManyToManyField(
                        blank=True, related_name="subtasks", to="tasks.task"
                    ),
                ),
                (
                    "task_owner",
                    models.ForeignKey(
                        default=0,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks_owned",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["task_heading"],},
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
                ("creation_date", models.DateTimeField(auto_now=True)),
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
                    "owned_tasks",
                    models.ManyToManyField(
                        blank=True, related_name="team_tasks_owned", to="tasks.task"
                    ),
                ),
                (
                    "team_owner",
                    models.ForeignKey(
                        default=0,
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
        migrations.AddField(
            model_name="user",
            name="owned_tasks",
            field=models.ManyToManyField(
                blank=True, related_name="task_owners", to="tasks.task"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="owned_teams",
            field=models.ManyToManyField(
                blank=True, related_name="team_owners", to="tasks.team"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.permission",
                verbose_name="user permissions",
            ),
        ),
    ]
