from django.test import TestCase
from django.urls import reverse
from tasks.forms import TaskForm
from tasks.models import User
from tasks.models import Task
logger = logging.getLogger(__name__)

class TaskCreationViewTestCase(TestCase):
    """Tests for the task creation view."""

    def setUp(self):
        self.url = reverse("create_task")
        self.form_data = {
            "task_heading": "Test Task",
            "task_description": "This is a test task.",
            "team_assigned": "team1",  # Assuming you have a team with the identifier "team1"
            "deadline_date": "2023-12-31",
            "task_complete": False,
            "priority": Task.PRIORITY_CHOICES[0][0],
        }

        # Create a user and log them in
        self.user = User.objects.create_user(
            username="@janedoe", password="123Password"
        )
        self.client.login(username="@janedoe", password="123Password")
    
    

    def test_task_creation_url(self):
        self.assertEqual(self.url, "/create_task/")

    def test_get_task_creation(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_task.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, TaskForm))
        self.assertFalse(form.is_bound)

    def test_successful_task_creation(self):
        before_count = Task.objects.count()
        # Pass the user instance when initializing the TaskForm
        form = TaskForm(user=self.user)
        response = self.client.post(self.url, {**self.form_data, "user": self.user}, follow=True)
        after_count = Task.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse("dashboard")
        self.assertRedirects(
            response, response_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "dashboard.html")
        task = Task.objects.get(task_heading="Test Task")
        self.assertEqual(task.task_description, "This is a test task.")
        # Add more assertions as needed for other task attributes

    def test_blank_task_creation_form(self):
        # Pass the user instance when initializing the TaskForm
        form = TaskForm(user=self.user)
        # Test submitting a form with blank fields
        before_count = Task.objects.count()
        response = self.client.post(reverse("create_task"), {**self.form_data, "user": self.user}, follow=True)
        after_count = Task.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_task.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, TaskForm))
        self.assertTrue(form.is_bound)
        self.assertTrue(form.errors)  # Check for form errors indicating required fields.

    # Add more test methods for different scenarios as needed
