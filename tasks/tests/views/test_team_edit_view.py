from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from tasks.models import Team, User
from tasks.forms import EditTeamForm
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from tasks.models import Team
from django.test import TestCase
from django.urls import reverse
from tasks.models import Task, Comment
from django.test import TestCase, RequestFactory
from django.urls import reverse
from tasks.models import Team
from tasks.views import show_user_information
from django.test import TestCase, Client
from django.utils import timezone
from tasks.models import Task
from django.urls import reverse
from django.test import TestCase, Client
from django.urls import reverse
from tasks.models import Task, Team
from datetime import datetime, timedelta
from django.utils import timezone
from tasks.views import dashboard


class TeamEditTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

        self.team_owner = User.objects.create_user(
            username="testuser123",
            email="testuser123@example.com",
            password="Password123",
        )
        self.team = Team.objects.create(
            team_name="Test Team",
            unique_identifier="#TestTeam",
            description="This is a test team.",
            team_owner=self.team_owner,
        )

    def test_edit_team_permission_denied(self):
        second_user = User.objects.create_user(
            username="anotheruser",
            password="anotherpassword",
            email="owner22user@example.com",
        )
        self.client.login(username="anotheruser", password="anotherpassword")
        response = self.client.get(reverse("edit_team", args=[self.team.id]))
        self.assertRedirects(response, reverse("team_management"))

    def test_edit_team_invalid_form_data(self):
        self.client.login(username="testuser123", password="Password123")
        response = self.client.get(reverse("edit_team", args=[self.team.id]))
        invalid_data = {
            "team_name": "",
            "unique_identifier": "",
            "description": "",
        }
        response = self.client.post(
            reverse("edit_team", args=[self.team.id]), data=invalid_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "team_name", "This field is required.")
        self.assertFormError(
            response, "form", "unique_identifier", "This field is required."
        )

    def test_edit_team_successful(self):
        self.client.login(username="owneruser", password="ownerpassword")
        response = self.client.get(reverse("edit_team", args=[self.team.id]))
        valid_data = {
            "team_name": "Updated Team Name",
            "unique_identifier": "#ABC",
            "description": "Updated Description",
        }
        response = self.client.post(
            reverse("edit_team", args=[self.team.id]), data=valid_data
        )
        self.assertRedirects(response, reverse("team_management"))


class TeamDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="123Password"
        )
        self.team = Team.objects.create(
            team_name="Test Team",
            description="Test Description",
            team_owner=self.user,
            unique_identifier="#ABC123",
        )

        self.client = Client()
        self.client.login(username="testuser", password="123Password")

    def test_team_delete_view(self):
        delete_team_url = reverse("team_delete", kwargs={"team_id": self.team.id})
        response = self.client.post(delete_team_url)
        self.assertRedirects(response, reverse("team_management"))
        team_database = Team.objects.filter(id=self.team.id).exists()
        self.assertFalse(team_database, "The team should have been deleted")


from django.test import TestCase, Client
from django.urls import reverse
from tasks.models import Invitation, User, Team


class NotificationsViewTest(TestCase):
    def setUp(self):
        user_requesting_to_join = User.objects.create(
            username="requesting_user", email="requesting_user@example.com"
        )
        user_creating_invitation = User.objects.create(
            username="creating_user", email="creating_user@example.com"
        )
        owner_user = User.objects.create(username="owner", email="owner@example.com")
        team_to_join = Team.objects.create(team_name="Test Team", team_owner=owner_user)

        Invitation.objects.create(
            user_requesting_to_join=user_requesting_to_join,
            user_creating_invitation=user_creating_invitation,
            team_to_join=team_to_join,
        )
        Invitation.objects.create(
            user_requesting_to_join=user_requesting_to_join,
            user_creating_invitation=user_creating_invitation,
            team_to_join=team_to_join,
        )

        self.client = Client()

    def test_notifications_view(self):
        notifications_url = reverse("notifications")
        response = self.client.get(notifications_url)
        self.assertTemplateUsed(response, "notifications.html")
        self.assertEqual(response.status_code, 200)
        expected_notifications = Invitation.objects.all()
        self.assertQuerysetEqual(
            response.context["mynotifications"], expected_notifications, ordered=False
        )


class ShowTeamViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username="testuser", email="test@example.com")
        self.team = Team.objects.create(team_name="Team Newt", team_owner=self.user)

    def test_show_team_valid_id(self):
        team_id = self.team.id
        url = reverse("show_team", kwargs={"team_id": team_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "show_team.html")
        self.assertEqual(response.context["team"], self.team)

    def test_show_team_invalid_id(self):
        invalid_team_id = 99989234
        url = reverse("show_team", kwargs={"team_id": invalid_team_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("team_management"))


class AddCommentViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="123Password", email="test@example.com"
        )
        self.test_team = Team.objects.create(
            team_name="Team Newt", description="A test team", team_owner=self.user
        )

        self.task = Task.objects.create(
            task_heading="Test Task",
            task_description="Description of the task",
            team_assigned=self.test_team,
            task_owner=self.user,
        )

    def test_add_comment_POST(self):
        self.client.login(username="testuser", password="123Password")
        comment_text = "This is a test comment."
        url = reverse("add_comment", args=[self.task.id])
        response = self.client.post(url, {"comment": comment_text})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard"))

    def test_add_comment_invalid_task_id(self):
        invalid_task_id = 1238323
        url = reverse("add_comment", args=[invalid_task_id])
        response = self.client.post(url, {"comment": "Invalid comment"})
        self.assertEqual(response.status_code, 404)


class ShowUserInformationViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client = Client()
        self.client.login(username="testuser", password="testpassword")
        self.team = Team.objects.create(
            team_name="Test Team", description="A test team", team_owner=self.user
        )

    def test_show_user_information(self):
        url = reverse("user_information")
        response = self.client.get("/user/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("user", response.context)
        self.assertIn("team_points", response.context)
        self.assertEqual(response.context["user"], self.user)
        points = {self.team: self.user.points}
        self.assertEqual(response.context["team_points"], points)


class UpdateCompleteStatusViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", points=25
        )
        self.team = Team.objects.create(
            team_name="Test Team",
            description="Test Description",
            team_owner=self.user,
            unique_identifier="#ABC123",
        )

        self.task = Task.objects.create(
            task_heading="Test Task",
            task_description="Test Description",
            team_assigned=self.team,
            task_owner=self.user,
            creation_date=timezone.now(),
            last_modified=timezone.now(),
            task_complete=False,
            status=Task.NOT_STARTED,
            priority=Task.LOW,
        )

        self.client = Client()
        self.client.login(username="testuser", password="testpassword")

    def test_update_complete_status_POST(self):
        url = reverse("update_task_status", kwargs={"task_id": self.task.id})
        data = {"new_status": Task.COMPLETED}
        response = self.client.post(url, data=data)
        updated_task = Task.objects.get(id=self.task.id)
        self.assertTrue(updated_task.task_complete)
        self.assertIsNotNone(updated_task.completion_time)
        self.assertRedirects(response, reverse("dashboard"))

    def test_update_task_status_POST_completed(self):
        url = reverse("update_task_status", kwargs={"task_id": self.task.id})
        data = {"new_status": "Completed"}
        response = self.client.post(url, data=data)
        updated_task = Task.objects.get(id=self.task.id)
        self.assertEqual(updated_task.status, "Completed")
        self.assertTrue(updated_task.task_complete)
        self.assertIsNotNone(updated_task.completion_time)
        self.assertEqual(updated_task.task_owner.points, 35)
        self.assertRedirects(response, reverse("dashboard"))

    def test_update_task_status_POST_in_progress(self):
        self.task.status = "Completed"
        self.task.task_complete = True
        self.task.save()
        url = reverse("update_task_status", kwargs={"task_id": self.task.id})
        data = {"new_status": "In Progress"}
        response = self.client.post(url, data=data)
        updated_task = Task.objects.get(id=self.task.id)
        self.assertEqual(updated_task.status, "In Progress")
        self.assertFalse(updated_task.task_complete)
        self.assertIsNone(updated_task.completion_time)
        updated_owner = User.objects.get(id=self.task.task_owner.id)
        self.assertEqual(updated_owner.points, 15)
        self.assertRedirects(response, reverse("dashboard"))

    def test_update_task_status_GET(self):
        url = reverse("update_task_status", kwargs={"task_id": self.task.id})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "dashboard.html")
        self.assertEqual(response.context["task"], self.task)


from django.test import TestCase, Client
from django.urls import reverse
from tasks.models import Task, Team
from datetime import datetime, timedelta
from django.utils import timezone
from tasks.views import dashboard


class DashboardViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

        self.team1 = Team.objects.create(
            team_name="Team 1",
            description="Description for Team 1",
            team_owner=self.user,
            unique_identifier="#T1",
        )
        self.team2 = Team.objects.create(
            team_name="Team 2",
            description="Description for Team 2",
            team_owner=self.user,
            unique_identifier="#T2",
        )

        self.task1 = Task.objects.create(
            task_heading="Task 1",
            task_description="Description for Task 1",
            team_assigned=self.team1,
            task_owner=self.user,
            creation_date=timezone.now(),
            last_modified=timezone.now(),
            task_complete=False,
            status=Task.NOT_STARTED,
            priority=Task.LOW,
        )
        self.task2 = Task.objects.create(
            task_heading="Task 2",
            task_description="Description for Task 2",
            team_assigned=self.team2,
            task_owner=self.user,
            creation_date=timezone.now() - timedelta(days=1),
            last_modified=timezone.now() - timedelta(days=1),
            task_complete=False,
            status=Task.IN_PROGRESS,
            priority=Task.HIGH,
        )

    def test_toggle_priority_order(self):
        url = reverse("dashboard")
        post_data = {"filter_tasks": "toggle_priority"}
        response = self.client.post(url, post_data)

    def test_toggle_display_settings(self):
        url = reverse("dashboard")
        post_data = {"filter_tasks": "toggle_low_priority"}
        response = self.client.post(url, post_data)
