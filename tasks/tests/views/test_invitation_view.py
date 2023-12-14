# test_invite_views.py
from django.test import TestCase, Client
from django.urls import reverse
from tasks.forms import TeamCreationForm
from tasks.models import Team
from tasks.models import User
from django.contrib.messages import get_messages
from tasks.models import  Invitation
class InviteUserViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user('user1', 'user1@example.com', 'password1')
        self.user2 = User.objects.create_user('user2', 'user2@example.com', 'password2')
        self.team = Team.objects.create(team_name="Test Team", description="A test team", team_owner=self.user1)
        self.invite_url = reverse('invite_user', args=[self.team.id, self.user1.id]) 

    def test_invite_user_view_with_existing_user(self):
        self.client.login(username='user1', password='password1')
        response = self.client.post(self.invite_url, {'input_username': 'user2'})
        self.assertEqual(response.status_code, 302)  
        self.assertTrue(Invitation.objects.filter(user_requesting_to_join=self.user2, team_to_join=self.team).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Successfully invited user user2")

    def test_invite_user_view_with_nonexistent_user(self):
        self.client.login(username='user1', password='password1')
        response = self.client.post(self.invite_url, {'input_username': 'nonexistentuser'})
        self.assertEqual(response.status_code, 302) 
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "User does not exist.")

    def test_invite_user_view_duplicate_request(self):
        pass