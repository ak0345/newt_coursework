from django.test import TestCase, Client
from django.urls import reverse
from tasks.models import Team, User


class LookupEverythingTestCase(TestCase):
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

    def test_lookup_everything_post(self):
        url = reverse("lookup-everything")
        data = {"everythingsearched": "TeamNewt"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("everythingsearched", response.context)
        self.assertIn("teamsfound", response.context)
        self.assertIn("usersfound", response.context)

    def test_lookup_everything_get(self):
        url = reverse("lookup-everything")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_leave_team(self):
        team_id = self.team.id
        response = self.client.post(reverse("leave_team", args=[team_id]))
        self.assertRedirects(response, reverse("team_management"))
        team = Team.objects.get(id=team_id)
        self.assertNotIn(self.user, team.users_in_team.all())

    def test_leave_team_redirect(self):
        self.team.users_in_team.add(self.user)
        response = self.client.post(reverse("leave_team", args=[self.team.id]))
        self.assertRedirects(response, reverse("team_management"))
