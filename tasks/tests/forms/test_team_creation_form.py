from django import forms
from django.test import TestCase
from tasks.forms import TeamCreationForm
from tasks.models import Team, User


class TeamCreationFormTestCase(TestCase):
    """Unit tests of the team creation form."""

    def setUp(self):
        self.form_input = {
            "team_name": "Newt",
            "unique_identifier": "#Newt",
            "description": "This is a sample team.",
        }
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_form_has_necessary_fields(self):
        form = TeamCreationForm()
        self.assertIn("team_name", form.fields)
        self.assertIn("unique_identifier", form.fields)
        self.assertIn("description", form.fields)

    def test_valid_team_creation_form(self):
        form = TeamCreationForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input["unique_identifier"] = "Newt"
        form = TeamCreationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = TeamCreationForm(data=self.form_input)
        before_count = Team.objects.count()
        form.save(user=self.user)
        after_count = Team.objects.count()
        self.assertEqual(after_count, before_count + 1)
        new_team = Team.objects.last()
        self.assertEqual(new_team.team_name, "Newt")
        self.assertEqual(new_team.unique_identifier, "#Newt")
        self.assertEqual(new_team.description, "This is a sample team.")

    def test_invalid_form_data(self):
        invalid_data = {
            "team_name": "",
            "unique_identifier": "",
            "description": "",
        }

        form = TeamCreationForm(data=invalid_data)
        self.assertFalse(form.is_valid())

        with self.assertRaises(ValueError) as context:
            form.save(user=self.user)

        self.assertEqual(str(context.exception), "Form data is not valid")
