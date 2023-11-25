from django.test import TestCase
from tasks.models import User, Team, Task
from django.utils import timezone
import datetime

class TaskModelTest(TestCase):

    def setUp(self):
        # Create instances of User and Team for testing
        test_user = User.objects.create(username='testuser', password='12345')
        test_team = Team.objects.create(team_name='Test Team', description='A test team')

        # Create a Task instance for testing
        self.task = Task.objects.create(
            task_heading='Test Task',
            task_description='A task for testing',
            team_assigned=test_team,
            task_owner=test_user,
            deadline_date=timezone.now() + datetime.timedelta(days=30)
        )

    def test_task_creation(self):
        self.assertEqual(self.task.task_heading, 'Test Task')
        self.assertEqual(self.task.task_description, 'A task for testing')
        self.assertEqual(self.task.team_assigned.team_name, 'Test Team')
        self.assertEqual(self.task.task_owner.username, 'testuser')
        self.assertFalse(self.task.task_complete)

    def test_task_string_representation(self):
        self.assertEqual(str(self.task), 'Test Task')

    def test_task_deadline(self):
        future_date = timezone.now() + datetime.timedelta(days=25)
        self.assertTrue(self.task.deadline_date > future_date)
