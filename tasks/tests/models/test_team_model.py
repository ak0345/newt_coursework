"""Unit tests for the Team model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from tasks.models import Team


class TeamModelTestCase(TestCase):
    fixtures = ["tasks/tests/fixtures/other_users.json"]

    def setUp(self):
        self.team = Team.objects.get(
            team_name="Newt"
        ) 

    def test_valid_team_creation(self):
        self._assert_team_is_valid()

    def test_team_name_cannot_be_blank(self):
        self.team.team_name = ""
        self._assert_team_is_invalid()

    def test_team_name_must_be_unique(self):
        second_team = Team.objects.get(team_name="Team_Newt")
        self.team.team_name = second_team.team_name
        self._assert_team_is_invalid()

    def test_team_name_can_be_100_characters_long(self):
        self.team.team_name = "@" + "x" * 99
        self._assert_team_is_valid()

    def test_team_name_cannot_be_over_100_characters_long(self):
        self.team.team_name = "@" + "x" * 100
        self._assert_team_is_invalid()

    def test_unique_identifier_must_be_unique(self):
        second_team = Team.objects.get(team_name="Team_Newt")
        self.team.unique_identifier = second_team.unique_identifier
        self._assert_team_is_invalid()

    def test_unique_identifier_starts_with_hashtag(self):
        self.team.unique_identifier = "unique_identifer_invalid"
        self._assert_team_is_invalid()

    def test_unique_identifier_must_have_at_least_three_alphanumericals(self):
        self.team.unique_identifier = "#ab"
        self._assert_team_is_invalid()

    def test_unique_identifier_must_contain_only_alphanumericals_after_hashtag(self):
        self.team.unique_identifier = "#Ne!wt"
        self._assert_team_is_invalid()

    def test_unique_identifier_must_contain_at_least_3_alphanumericals_after_hashtag(
        self,
    ):
        self.team.unique_identifier = "#Ne"
        self._assert_team_is_invalid()

    def test_unique_identifier_must_contain_only_one_hastag(self):
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
