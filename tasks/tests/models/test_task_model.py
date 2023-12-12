"""Unit tests for the Task model."""
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
import datetime

from tasks.models import User, Team, Task


class TaskModelTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create(username='@testuser', password='12345', email='test@example.com')
        self.test_team = Team.objects.create(team_name='Test Team', description='A test team', team_owner=self.test_user)
        self.future_days = 30
        self.task = Task.objects.create(
            task_heading='Test Task',
            task_description='A task for testing',
            team_assigned=self.test_team,
            task_owner=self.test_user,
            deadline_date=timezone.now() + datetime.timedelta(days=self.future_days)
        )

    def test_task_creation(self):
        self.assertEqual(self.task.task_heading, 'Test Task')
        self.assertEqual(self.task.task_description, 'A task for testing')
        self.assertEqual(self.task.team_assigned.team_name, 'Test Team')
        self.assertEqual(self.task.task_owner.username, '@testuser')
        self.assertFalse(self.task.task_complete)

    def test_task_string_representation(self):
        self.assertEqual(str(self.task), 'Test Task')

    def test_task_deadline(self):
        future_date = timezone.now() + datetime.timedelta(days=25)
        self.assertTrue(self.task.deadline_date > future_date)

    def test_correct_deadline_date(self):
        expected_deadline = timezone.now() + datetime.timedelta(days=self.future_days)
        self.assertTrue(abs(self.task.deadline_date - expected_deadline) < datetime.timedelta(seconds=1), "The deadline date is not correctly set")

    def test_task_completion_status_change(self):
        self.assertFalse(self.task.task_complete)
        self.task.task_complete = True
        self.task.save()
        self.assertTrue(Task.objects.get(id=self.task.id).task_complete)

    def test_task_owner_assignment(self):
        self.assertEqual(self.task.task_owner, self.test_user)

    def test_task_team_assignment(self):
        self.assertEqual(self.task.team_assigned, self.test_team)

def test_past_deadline_date(self):
    past_date = timezone.now() - datetime.timedelta(days=5)
    task = Task(
        task_heading='Past Task',
        task_description='A task with past deadline',
        team_assigned=self.test_team,
        task_owner=self.test_user,
        deadline_date=past_date
    )
    with self.assertRaises(ValidationError):
        task.full_clean()


    def test_task_update(self):
        new_heading = "Updated Task Heading"
        self.task.task_heading = new_heading
        self.task.save()
        self.assertEqual(Task.objects.get(id=self.task.id).task_heading, new_heading)