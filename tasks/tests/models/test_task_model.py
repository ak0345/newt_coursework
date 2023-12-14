"""Unit tests for the Task model."""
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
import datetime
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

    def setUp(self):
        self.test_user = User.objects.create(username='@testuser', password='12345', email='test@example.com')
        self.test_team = Team.objects.create(team_name='Test Team', description='A test team', team_owner=self.test_user)
        self.future_days = 30
        self.test_team.users_in_team.add(self.test_user)
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

    def test_create_task_via_form(self):
        user1, user2 = self.create_users()

        team = self.create_team(user1, users=[user1, user2])
    def test_priority_choices(self):
        for priority, _ in Task.PRIORITY_CHOICES:
            self.task.priority = priority
            self.task.save()
            self.assertEqual(Task.objects.get(id=self.task.id).priority, priority)

    def test_status_and_deadline(self):
        self.task.status = Task.COMPLETED
        self.task.deadline_date = timezone.now() - datetime.timedelta(days=1)
        self.task.save()
        task_retrieved = Task.objects.get(id=self.task.id)
        self.assertEqual(task_retrieved.status, Task.COMPLETED)
        self.assertTrue(task_retrieved.deadline_date < timezone.now())

    def test_task_owner(self):
        self.assertEqual(self.task.task_owner, self.test_user)

    def test_users_assigned_are_in_team(self):
        user1,user2 = self.create_users()
        team = self.create_team(user2, users=[user1])
        user_not_in_team = User.objects.create(username='@otheruser', password='12345', email='other@example.com')
        self.task.user_assigned.add(self.test_user)
        self.task.user_assigned.add(user_not_in_team)
        self.assertIn(self.test_user, self.task.team_assigned.users_in_team.all())
        self.assertNotIn(user_not_in_team, self.task.team_assigned.users_in_team.all())

        new_task = Task.objects.create(
            task_heading= "Test Task",
            task_description= "This is a test task.",
            task_owner= user1,
            team_assigned= team,
            deadline_date= "2023-12-31",
            task_complete= False,
            priority= "High"
        )
        new_task.user_assigned.set([user2])
        self.assertEqual(new_task.task_heading, "Test Task")
        self.assertEqual(new_task.task_owner, user1)
        self.assertEqual(list(new_task.user_assigned.all()), [user2])
        self.assertEqual(new_task.task_owner, user1)

    def test_completion_time_consistency(self):
        self.task.task_complete = True
        completion_time_now = timezone.now()
        self.task.completion_time = completion_time_now
        self.task.save()
        self.assertTrue(abs(Task.objects.get(id=self.task.id).completion_time - completion_time_now) < datetime.timedelta(seconds=1), "Completion time is not consistent with the expected time")
