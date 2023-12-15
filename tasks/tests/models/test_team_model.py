"""Unit tests for the Team model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from tasks.models import Team, User
from django.utils import timezone


class TeamModelTestCase(TestCase):
    #fixtures = ["tasks/tests/fixtures/other_users.json"]

    def setUp(self):
        self.user1 = User.objects.create(
            username='@testuser',
            first_name='Test',
            last_name='User',
            email='test@example.com'
        )
        self.user2 = User.objects.create(
            username='@testuser2',
            first_name='Test',
            last_name='User',
            email='test2@example.com'
        )
        self.user3 = User.objects.create(
            username='@testuser3',
            first_name='Test',
            last_name='User',
            email='test3@example.com'
        )

        # Create a test team with the test user as the team owner
        self.team = Team.objects.create(
            team_name='Test Team',
            description='Team description',
            team_owner=self.user1,
            unique_identifier='#abc123',
            creation_date=timezone.now()
        )
        self.team.users_in_team.set([self.user2,self.user3])

        self.second_team = Team.objects.create(
            team_name='Test Team2',
            description='Team description2',
            team_owner=self.user2,
            unique_identifier='#abc12322',
            creation_date=timezone.now()
        )
        self.team.users_in_team.set([self.user1,self.user3])

    def test_valid_team_creation(self):
        self._assert_team_is_valid()

    def test_team_name_cannot_be_blank(self):
        self.team.team_name = ""
        self._assert_team_is_invalid()

    def test_team_name_can_be_100_characters_long(self):
        self.team.team_name = "@" + "x" * 99
        self._assert_team_is_valid()

    def test_team_name_cannot_be_over_100_characters_long(self):
        self.team.team_name = "@" + "x" * 100
        self._assert_team_is_invalid()

    def test_unique_identifier_must_be_unique(self):
        self.team.unique_identifier = self.second_team.unique_identifier
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
    
    def test_calculate_team_points(self):
        # Create a team with the user as the team owner
        test_team = self.team

        # Add some points to the user and include the user in the team
        self.user1.points += 50
        test_team.users_in_team.set([self.user2, self.user3])

        # Calculate team points and assert that it's correct
        calculated_points = test_team.calculate_team_points()
        expected_points = self.user1.points
        for user in test_team.users_in_team.all():
            expected_points+=user.points
        self.assertEqual(calculated_points, expected_points)
        
