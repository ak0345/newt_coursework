from django.test import TestCase
from tasks.forms import TaskForm, EditTaskForm
from tasks.models import User, Task, Team


class TaskFormTest(TestCase):
    def setUp(self):
        # Create some sample data, such as a user and a team
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.team = Team.objects.create(
            team_owner=self.user,
            team_name="Newt",
            unique_identifier="#Newt",
            description="This is a sample team.",
        )
        # Create other necessary objects as needed

    def test_valid_task_form(self):
        form_data = {
            "task_heading": "Test Task",
            "task_description": "This is a test task.",
            "user_assigned": [self.user],
            "team_assigned": self.team,
            "deadline_date": "2023-12-31",
            "task_complete": False,
            "priority": "High",
        }
        form = TaskForm(data=form_data)
        editform = EditTaskForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(editform.is_valid(), form.errors)

    def test_invalid_task_form(self):
        # Test with invalid data, for example, missing task_heading
        form_data = {
            "task_description": "This is a test task.",
            #'user_assigned': [self.user.id],
            "team_assigned": 1,
            "deadline_date": "2023-12-31",
            "task_complete": False,
        }
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "task_heading", form.errors.keys()
        )  # Check if 'task_heading' is in the error messages
        editform = EditTaskForm(data=form_data)
        self.assertFalse(editform.is_valid())
        self.assertIn(
            "task_heading", editform.errors.keys()
        )  # Check if 'task_heading' is in the error messages
