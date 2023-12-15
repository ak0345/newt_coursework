from django.test import TestCase, Client
from django.urls import reverse
from tasks.models import Team, User


class LookupTeamTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="@janedoe", password="123Password"
        )
        self.client = Client()
        self.team = Team.objects.create(
            team_name="TeamNewt",
            unique_identifier="#TeamNewt",
            description="This is TeamNewt.",
            team_owner=self.user,
        )

    def test_lookup_team_post(self):
        url = reverse("lookup-team")
        data = {"teamsearched": "TeamNewt"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("teamsearched", response.context)
        self.assertIn("teamsfound", response.context)

    def test_lookup_everything_get(self):
        url = reverse("lookup-team")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
