from django.test import TestCase
from django.urls import reverse
from tasks.forms import TeamCreationForm
from tasks.models import Team
from tasks.models import User


class TeamCreationViewTestCase(TestCase):
    """Tests of the team creation view."""

    def setUp(self):
        self.url = reverse("create_team")
        self.form_input = {
            "team_name": "Team_2",
            "unique_identifier": "#Unique2",
            "description": "B",
        }

        self.user = User.objects.create_user(
            username="@janedoe", password="123Password"
        )
        self.client.login(username="@janedoe", password="123Password")

    def test_team_creation_url(self):
        self.assertEqual(self.url, "/create_team/")

    def test_get_team_creation(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_team.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, TeamCreationForm))
        self.assertFalse(form.is_bound)

    def test_unsuccesful_team_creation(self):
        self.form_input["unique_identifier"] = "unique2"
        before_count = Team.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Team.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_team.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, TeamCreationForm))
        self.assertTrue(form.is_bound)

    def test_successful_team_creation(self):
        before_count = Team.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Team.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse("team_management")
        self.assertRedirects(
            response, response_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "team_management.html")
        team = Team.objects.get(team_name="Team_2")
        self.assertEqual(team.unique_identifier, "#Unique2")
        self.assertEqual(team.description, "B")
