from django.test import TestCase
from tasks.models import User, Team, Invitation
from tasks.forms import InvitationForm

class InvitationFormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1",
            password="password1",
            email="user1@example.com"
        )

        self.team = Team.objects.create(
            team_name="Test Team",
            unique_identifier="test-team",
            description="This is a test team.",
            team_owner=self.user
        )
        self.inviting_user = User.objects.create_user(
            username="user2",
            password="password2",
            email="user2@example.com" 
        )

    def test_invalid_invitation_form(self):
        form_data = {}  
        form = InvitationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_valid_invitation_form_and_save(self):

        form_data = {
            "user_requesting_to_join": self.user.id,
            "team_to_join": self.team.id,
        }

 
        form = InvitationForm(data=form_data)
        self.assertTrue(form.is_valid())
        invitation = form.save(
            user=self.user,
            team=self.team,
            inviting=self.inviting_user,
            commit=True 
        )

        self.assertEqual(invitation.user_requesting_to_join, self.user)
        self.assertEqual(invitation.team_to_join, self.team)
        self.assertEqual(invitation.user_creating_invitation, self.inviting_user)

        invitation_from_db = Invitation.objects.get(pk=invitation.pk)
        self.assertEqual(invitation_from_db, invitation)

    def test_valid_invitation_form_no_save(self):
        form_data = {
            "user_requesting_to_join": self.user.id,
            "team_to_join": self.team.id,
        }

        form = InvitationForm(data=form_data)
        self.assertTrue(form.is_valid())
        invitation = form.save(
        user=self.user,
        team=self.team,
        inviting=self.inviting_user,
        commit=False
    )
        existing_invitations = Invitation.objects.filter(pk=invitation.pk)
        self.assertFalse(existing_invitations.exists())

        
