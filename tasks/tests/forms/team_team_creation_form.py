from django.test import TestCase
from tasks.models import User, Team
from tasks.forms import TeamCreationForm, EditTeamForm

class TeamCreationFormTestCase(TestCase):
    """Unit tests of the team creation form."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword"
        )

    def test_valid_team_creation_form(self):
        form_data = {
            "team_name": "Test Team",
            "unique_identifier": "test-identifier", 
            "description": "This is a test team.",
        }
        form = TeamCreationForm(data=form_data)
        form.is_valid() 
        team = form.save(user=self.user, commit=False) 
        self.assertEqual(team.team_name, "Test Team")
        self.assertEqual(team.unique_identifier, "test-identifier")
        self.assertEqual(team.description, "This is a test team.")
        self.assertEqual(team.team_owner, self.user)


class EditTeamFormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword"
        )
        self.team = Team.objects.create(
            team_name="Old Team",
            unique_identifier="old-identifier",
            description="This is an old team.",
            team_owner=self.user
        )

    def test_valid_edit_team_form(self):
        form_data = {
            "team_name": "Updated Team",
            "unique_identifier": "updated-identifier",  
            "description": "This is an updated team.",
        }
        form = EditTeamForm(data=form_data, instance=self.team)
        form.is_valid()  
        updated_team = form.save(user=self.user, team_instance=self.team) 
        self.assertEqual(updated_team.team_name, "Updated Team")
        self.assertEqual(updated_team.unique_identifier, "updated-identifier")
        self.assertEqual(updated_team.description, "This is an updated team.")


    def test_invalid_edit_team_form(self):
        form_data = {
            "team_name": "", 
            "unique_identifier": "updated-identifier",
            "description": "This is an updated team.",
        }
        form = EditTeamForm(data=form_data, instance=self.team)
        self.assertFalse(form.is_valid()) 
