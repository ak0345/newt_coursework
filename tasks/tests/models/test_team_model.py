"""Unit tests for the Team model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from tasks.models import Team, User


class TeamModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='user', email='user@example.com', password='password')
        self.team = Team.objects.create(
            team_name="Newt",
            description="A description for Newt",
            unique_identifier="#Newt123",
            team_owner=self.user
        )

    def test_valid_team_creation(self):
        self._assert_team_is_valid()

    def test_team_name_cannot_be_blank(self):
        self.team.team_name = ""
        self._assert_team_is_invalid()

    def test_team_name_must_be_unique(self):
        Team.objects.create(
            team_name="Team_Newt",
            description="Another description",
            unique_identifier="#Newt456",
            team_owner=self.user
        )
        self.team.team_name = "Team_Newt"
        self._assert_team_is_invalid()

    def test_team_name_can_be_100_characters_long(self):
        self.team.team_name = "@" + "x" * 99
        self._assert_team_is_valid()

    def test_team_name_cannot_be_over_100_characters_long(self):
        self.team.team_name = "@" + "x" * 100
        self._assert_team_is_invalid()

    def test_unique_identifier_must_be_unique(self):
        Team.objects.create(
            team_name="UniqueTeam",
            description="Unique team description",
            unique_identifier="#Unique123",
            team_owner=self.user
        )
        self.team.unique_identifier = "#Unique123"
        self._assert_team_is_invalid()

    def test_unique_identifier_starts_with_hashtag(self):
        self.team.unique_identifier = "unique_identifier_invalid"
        self._assert_team_is_invalid()

    def test_unique_identifier_must_have_at_least_three_alphanumericals(self):
        self.team.unique_identifier = "#ab"
        self._assert_team_is_invalid()

    def test_unique_identifier_must_contain_only_alphanumericals_after_hashtag(self):
        self.team.unique_identifier = "#Ne!wt"
        self._assert_team_is_invalid()

    def test_unique_identifier_must_contain_at_least_3_alphanumericals_after_hashtag(self):
        self.team.unique_identifier = "#Ne"
        self._assert_team_is_invalid()

    def test_unique_identifier_must_contain_only_one_hashtag(self):
        self.team.unique_identifier = "##Newt"
        self._assert_team_is_invalid()

    def test_description_cannot_be_blank(self):
        self.team.description = ""
        self._assert_team_is_invalid()

    def _assert_team_is_valid(self):
        try:
            self.team.full_clean()
        except ValidationError:
            self.fail("Test team should be valid")

    def _assert_team_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.team.full_clean()
