from django.core.management.base import BaseCommand
from faker import Faker
import pytz
from random import randint, choice, choices
from tasks.models import Task, Team, Comment, Invitation,User


user_fixtures = [
    {
        "username": "@johndoe",
        "email": "john.doe@example.org",
        "first_name": "John",
        "last_name": "Doe",
        "is_staff": True,
        "is_superuser": False,

    },
    {
        "username": "@janedoe",
        "email": "jane.doe@example.org",
        "first_name": "Jane",
        "last_name": "Doe",
        "is_superuser": True,
        "is_staff": True
    },
    {
        "username": "@charlie",
        "email": "charlie.johnson@example.org",
        "first_name": "Charlie",
        "last_name": "Johnson",
        "is_superuser": True,
        "is_staff": False,
    },
]

def create_username(first_name, last_name):
    return "@" + first_name.lower() + last_name.lower()


def create_email(first_name, last_name):
    return first_name + "." + last_name + "@example.org"

class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 100
    DEFAULT_PASSWORD = "Password123"
    TASK_COUNT = 100
    TEAM_COUNT = 100
    COMMENT_COUNT = 100
    INVITATION_COUNT = 20
    help = "Seeds the database with sample data"

    def __init__(self):
        self.faker = Faker("en_GB")

    def handle(self, *args, **options):
        for user in user_fixtures:
            self.create_user(user)
        self.create_users()
        self.create_teams()
        self.create_tasks()
        self.create_comments()
        self.create_invitations()

    def create_tasks(self):
        task_count = Task.objects.count()
        while task_count < self.TASK_COUNT:
            print(f"Seeding tasks {task_count}/{self.TASK_COUNT}", end="\r")
            self.generate_task()
            task_count = Task.objects.count()
        print("Task seeding complete.      ")

    def generate_task(self):
        task_heading = self.faker.sentence()
        task_description = self.faker.text()
        team_assigned = choice(Team.objects.all())
        task_owner = choice(User.objects.all())
        deadline_date = self.faker.date_time_this_month(tzinfo=pytz.UTC)
        task_complete = self.faker.boolean()
        completion_time = self.faker.date_time_this_month(tzinfo=pytz.UTC)
        status = choice([choice[0] for choice in Task.STATUS_CHOICES])
        priority = choice([choice[0] for choice in Task.PRIORITY_CHOICES])

        Task.objects.create(
            task_heading=task_heading,
            task_description=task_description,
            team_assigned=team_assigned,
            task_owner=task_owner,
            deadline_date=deadline_date,
            task_complete=task_complete,
            completion_time=completion_time,
            status=status,
            priority=priority,
        )

    def create_teams(self):
        team_count = Team.objects.count()
        while team_count < self.TEAM_COUNT:
            print(f"Seeding teams {team_count}/{self.TEAM_COUNT}", end="\r")
            self.generate_team()
            team_count = Team.objects.count()
        print("Team seeding complete.      ")

    def generate_team(self):
        team_name = self.faker.word()
        description = self.faker.text()
        team_owner = choice(User.objects.all())
        unique_identifier = "#" + self.faker.unique.word()

        team = Team.objects.create(
            team_name=team_name,
            description=description,
            team_owner=team_owner,
            unique_identifier=unique_identifier,
        )

        team.users_in_team.set(choices(User.objects.all(), k=randint(2, 5)))

    def create_comments(self):
        comment_count = Comment.objects.count()
        while comment_count < self.COMMENT_COUNT:
            print(f"Seeding comments {comment_count}/{self.COMMENT_COUNT}", end="\r")
            self.generate_comment()
            comment_count = Comment.objects.count()
        print("Comment seeding complete.      ")

    def generate_comment(self):
        task = choice(Task.objects.all())
        text = self.faker.text()

        Comment.objects.create(
            task=task,
            text=text,
        )

    def create_invitations(self):
        invitation_count = Invitation.objects.count()
        while invitation_count < self.INVITATION_COUNT:
            print(f"Seeding invitations {invitation_count}/{self.INVITATION_COUNT}", end="\r")
            self.generate_invitation()
            invitation_count = Invitation.objects.count()
        print("Invitation seeding complete.      ")

    def generate_invitation(self):
        user_requesting_to_join = choice(User.objects.all())
        user_creating_invitation = choice(User.objects.all())
        team_to_join = choice(Team.objects.all())

        Invitation.objects.create(
            user_requesting_to_join=user_requesting_to_join,
            user_creating_invitation=user_creating_invitation,
            team_to_join=team_to_join,
        )

    def create_users(self):
        user_count = User.objects.count()
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end="\r")
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        self.try_create_user(
            {
                "username": username,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "is_staff": False,
                "is_superuser": False,
            }
        )

    def try_create_user(self, data):
        try:
            self.create_user(data)
        except Exception as e:
            print(f"Error creating user: {e}")

    def create_user(self, data):
        User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=Command.DEFAULT_PASSWORD,
            first_name=data["first_name"],
            last_name=data["last_name"],
            is_staff=data["is_staff"],
            is_superuser=data["is_superuser"],
        )
