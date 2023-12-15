"""Tests of the task related views."""
from django.test import TestCase
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from tasks.models import User, Task, Team
from django.utils import timezone


class TaskViewTest(TestCase):
    def create_users(self):
        user1 = User.objects.create(
            first_name='Jane',
            last_name='Doe',
            username='@janedoe',
            email='janedoe@example.org',
            password=make_password('password123'),  # Set a password for the user
        )
        user2 = User.objects.create(
            first_name='Jane2',
            last_name='Doe2',
            username='@janedoe2',
            email='janedoe2@example.org',
            password=make_password('password456'),  # Set a password for the user
        )

        return [user1, user2]

    def create_team(self, owner, **kwargs):
        team = Team.objects.create(
            team_name='newt',
            description='New Team',
            unique_identifier='#wdqd',
            team_owner=owner
        )
        team.users_in_team.set(kwargs['users'])

        return team

    def test_create_task_view_get(self):
        user1, user2 = self.create_users()

        self.client.login(username=user1.username, password='password123')  # Use the password

        response = self.client.get("/create_task/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_task.html")

    def test_create_task_view_post(self):
        user1, user2 = self.create_users()

        team = self.create_team(user1, users=[user1, user2])

        self.client.login(username=user1.username, password='password123')  # Use the password

        form_data = {
            'task_heading': 'Test Task',
            'task_description': 'This is a test task.',
            'user_assigned': [user1.id, user2.id], 
            'team_assigned': team.id, 
            'deadline_date': timezone.now() + timezone.timedelta(days=3),
            'priority': 'High',
        }


        response = self.client.post(reverse('create_task'), data=form_data)

        print(response.content.decode('utf-8'))

        # Assert that the response redirects to the dashboard
        self.assertRedirects(response, reverse('dashboard'))

        # Assert that a task has been created
        self.assertEqual(Task.objects.count(), 1)
