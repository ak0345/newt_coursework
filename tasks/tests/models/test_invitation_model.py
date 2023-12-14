# test_invitation_model.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from tasks.models import User, Team, Invitation

class InvitationModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1', email='user1@example.com')
        self.user2 = User.objects.create_user(username='user2', password='password2', email='user2@example.com')
        self.team = Team.objects.create(team_name="Test Team", description="A test team", team_owner=self.user1)

        # Create a test invitation
        self.invitation = Invitation.objects.create(
            user_requesting_to_join=self.user1,
            user_creating_invitation=self.user2,
            team_to_join=self.team
        )

    def test_invitation_creation(self):
        self.assertEqual(self.invitation.user_requesting_to_join, self.user1)
        self.assertEqual(self.invitation.user_creating_invitation, self.user2)
        self.assertEqual(self.invitation.team_to_join, self.team)

    def test_string_representation(self):
        pass

    def test_invitation_integrity(self):
        pass
'''
    def test_no_duplicate_invitations(self):
        # Test that duplicate invitations cannot be created
        with self.assertRaises(ValidationError):
            Invitation.objects.create(
                user_requesting_to_join=self.user1,
                user_creating_invitation=self.user2,
                team_to_join=self.team
            )'''
"""
    def test_invite_nonexistent_user(self):
        # Create a form with data for a nonexistent user
        form_data = {
            "user_requesting_to_join": 99999,  # Nonexistent user ID
            "user_creating_invitation": self.user2.id,
            "team_to_join": self.team.id,
        }
        form = InvitationForm(data=form_data)
        # Check if the form is not valid due to nonexistent user
        self.assertFalse(form.is_valid())


    def test_accept_invite_adds_user_to_team(self):
        # Test that accepting an invite adds the user to the team
        # This requires implementation of an accept method on the Invitation model
        self.invitation.accept()
        self.assertIn(self.user1, self.team.members.all())

    def test_accept_invite_deletes_invitation(self):
        # Test that accepting an invite deletes the invitation
        self.invitation.accept()
        with self.assertRaises(Invitation.DoesNotExist):
            Invitation.objects.get(id=self.invitation.id)

    def test_reject_invite_does_not_add_user_to_team(self):
        # Test that rejecting an invite does not add the user to the team
        self.invitation.reject()
        self.assertNotIn(self.user1, self.team.members.all())

    def test_reject_invite_deletes_invitation(self):
        # Test that rejecting an invite deletes the invitation
        self.invitation.reject()
        with self.assertRaises(Invitation.DoesNotExist):
            Invitation.objects.get(id=self.invitation.id)

    def test_only_team_owner_can_invite(self):
        # Test that only the team owner can send invitations
        with self.assertRaises(ValidationError):
            Invitation.objects.create(
                user_requesting_to_join=self.user1,
                user_creating_invitation=User.objects.create_user(username='non_owner_user'),
                team_to_join=self.team
            )
"""