"""Unit tests for the Task model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from tasks.models import User, Task, Team
from tasks.forms import TaskForm


class TaskModelTest(TestCase):
    def create_users(self):
        user1 = User.objects.create(
            first_name="Jane",
            last_name="Doe",
            username="@janedoe",
            email="janedoe@example.org",
            password="testPassword",
        )
        user2 = User.objects.create(
            first_name="Jane2",
            last_name="Doe2",
            username="@janedoe2",
            email="janedoe2@example.org",
        )
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.team = Team.objects.create(
            team_owner=self.user,
            team_name="Newt",
            unique_identifier="#Newt",
            description="This is a sample team.",
        )

        return [user1, user2]

    def create_team(self, owner, **kwargs):
        team = Team.objects.create(
            team_name="newt",
            description="New Team",
            unique_identifier="#wdqd",
            team_owner=owner,
        )

        team.users_in_team.set(kwargs["users"])

        return team

    def test_create_task_via_form(self):
        user1, user2 = self.create_users()

        team = self.create_team(user1, users=[user1, user2])

        self.client.login(username=user1.username, password=user1.password)

        form_data = {
            "task_heading": "Test Task",
            "task_description": "This is a test task.",
            "user_assigned": [user1.id, user2.id],
            "team_assigned": team.id,
            "deadline_date": "2023-12-31",
            "task_complete": False,
            "priority": "High",
        }
        form = TaskForm(data=form_data)
        self.assertTrue(form.is_valid())
        new_task = form.save(user=user1)
        self.assertEqual(new_task.task_heading, "Test Task")
        self.assertEqual(new_task.task_owner, user1)
        self.assertEqual(list(new_task.user_assigned.all()), [user1, user2])
        self.assertEqual(new_task.task_owner, user1)
