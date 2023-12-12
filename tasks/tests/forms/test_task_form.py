from django.test import TestCase
from tasks.models import User, Team, Task, SubTask
from tasks.forms import TaskForm

class TaskFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.team = Team.objects.create(unique_identifier='team1', team_owner=self.user)

    def test_task_form_invalid_data(self):
        form_data = {
            'task_heading': 'Test Task',
            'task_description': 'This is a test task.',
            'user_assigned': [self.user.pk],
            'team_assigned': str(self.team.pk),
            'deadline_date': '2023-12-31',
            'task_complete': False,
            'priority': Task.PRIORITY_CHOICES[0][0],
        }

        form = TaskForm(data=form_data, user=self.user)
        is_valid = form.is_valid()
        self.assertFalse(is_valid)

        if is_valid:
            form.save()
        else:
            print("Form Errors:", form.errors)

    def test_task_form_valid_data(self):
        form_data = {
            'task_heading': 'Test Task',
            'task_description': 'This is a test task.',
            'user_assigned': [self.user.pk],
            'team_assigned': str(self.team.pk),
            'deadline_date': '2023-12-31',
            'task_complete': False,
            'priority': Task.PRIORITY_CHOICES[0][0],
        }

        form = TaskForm(data=form_data, user=self.user)
        if form.is_valid():
            task = form.save()
            self.assertEqual(task.task_heading, 'Test Task')
            self.assertEqual(task.task_owner, self.user)
            self.assertEqual(task.team_assigned, self.team)
        else:
            print("Form Errors:", form.errors)
            self.fail("Form data is not valid")

    def test_set_team_assigned_queryset(self):
        form = TaskForm(user=self.user)
        form.set_team_assigned_queryset(self.user)
        self.assertQuerysetEqual(form.fields['team_assigned'].queryset, [self.team])





"""
        # Create instances of SubTask or the related model
        self.subtask1 = SubTask.objects.create(...)  # Add relevant fields and values
        self.subtask2 = SubTask.objects.create(...)  # Add relevant fields and values


 # Verify the sub_tasks are correctly assigned
            self.assertIn(self.subtask1, task.sub_tasks.all())
            self.assertIn(self.subtask2, task.sub_tasks.all())"""

