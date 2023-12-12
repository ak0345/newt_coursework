from django.test import TestCase
from django.utils import timezone
from tasks.models import User, Team, Task
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
            'sub_tasks': ['Subtask 1', 'Subtask 2'],
            'priority': Task.PRIORITY_CHOICES[0][0],
        }

        form = TaskForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())

        if not form.is_valid():
            print(form.errors)
        task = form.save()

    def test_task_form_valid_data(self):
        form_data = {
            'task_heading': 'Test Task',
            'task_description': 'This is a test task.',
            'user_assigned': [self.user.pk],
            'team_assigned': str(self.team.pk),
            'deadline_date': '2023-12-31',
            'task_complete': False,
            'sub_tasks': ['Subtask 1', 'Subtask 2'],
            'priority': Task.PRIORITY_CHOICES[0][0],
        }

        form = TaskForm(data=form_data, user=self.user)

        task = form.save()

        if not form.is_valid():
            print(form.errors) 

        self.assertEqual(task.task_heading, 'Test Task')
        self.assertEqual(task.task_owner, self.user)
        self.assertEqual(task.team_assigned, self.team)

    def test_set_team_assigned_queryset(self):
        form = TaskForm(user=self.user)
        form.set_team_assigned_queryset(self.user)
        self.assertQuerysetEqual(form.fields['team_assigned'].queryset, [self.team])

    def save(self, commit=True):
        new_task = super(TaskForm, self).save(commit=False)
        if self.user:
            new_task.task_owner = self.user

        new_task.save()
        new_task.user_assigned.set(self.cleaned_data["user_assigned"])
        return new_task
