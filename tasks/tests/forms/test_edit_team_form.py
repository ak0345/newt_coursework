from django.test import TestCase
from tasks.forms import EditTeamForm
from tasks.models import Team, User


class EditTeamFormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.team = Team.objects.create(
            team_name="Newt",
            unique_identifier="#Newt",
            description="This is a sample team.",
            team_owner=self.user,
        )
        self.form_input = {
            "team_name": "Updated Team Name",
            "unique_identifier": "#UpdatedTeam",
            "description": "This is an updated description.",
        }

    def test_form_has_necessary_fields(self):
        form = EditTeamForm(instance=self.team)
        self.assertIn("team_name", form.fields)
        self.assertIn("unique_identifier", form.fields)
        self.assertIn("description", form.fields)

    def test_valid_edit_team_form(self):
        form = EditTeamForm(data=self.form_input, instance=self.team)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input["unique_identifier"] = "Newt"
        form = EditTeamForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_saves_correctly(self):
        form = EditTeamForm(data=self.form_input, instance=self.team)
        form.is_valid()  # Ensure form is valid before calling save()
        before_count = Team.objects.count()
        form.save(user=self.user, team_instance=self.team)
        after_count = Team.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(self.team.team_name, "Updated Team Name")
        self.assertEqual(self.team.unique_identifier, "#UpdatedTeam")
        self.assertEqual(self.team.description, "This is an updated description.")
