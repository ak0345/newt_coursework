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

class RemoveUserFromTeamTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.com", password="Password123"
        )
        self.user_being_removed = User.objects.create_user(
            username="user_being_removed",
            email="user@example.com",
            password="user_password",
        )
        self.team = Team.objects.create(team_owner=self.owner, team_name="Test Team")
        self.team.users_in_team.add(self.user_being_removed)

    def test_remove_user_from_team(self):
        self.client.force_login(self.owner)
        self.client.login(username="owner", password="Password123")
        url = reverse(
            "remove_user_from_team", args=(self.team.id, self.user_being_removed.id)
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        redirected_url = response.url
        redirected_response = self.client.get(redirected_url)
        self.assertEqual(redirected_response.status_code, 200)
        self.assertFalse(self.user_being_removed in self.team.users_in_team.all())
        self.assertContains(
            redirected_response,
            f"{self.user_being_removed.username} has been removed from the team.",
        )

    def test_remove_user_from_team_as_non_owner(self):
        non_owner = User.objects.create_user(username="non_owner")
        self.client.force_login(non_owner)
        url = reverse(
            "remove_user_from_team", args=(self.team.id, self.user_being_removed.id)
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        redirected_url = response.url
        redirected_response = self.client.get(redirected_url)
        self.assertEqual(redirected_response.status_code, 200)
        self.assertTrue(self.user_being_removed in self.team.users_in_team.all())
        self.assertContains(
            redirected_response, "Only the team owner can remove members from the team."
        )
