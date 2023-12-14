from django.core.management.base import BaseCommand
from faker import Faker
import pytz
from random import randint, choice, choices
from tasks.models import Task, Team, Comment, Invitation,User


user_fixtures = [
    {
        "username": "@johndoe",
        "email": "john.doe@example.org",
        "password" : "Password123",
        "first_name": "John",
        "last_name": "Doe",
        "is_superuser": False,
        "is_staff": True,

    },
    {
        "username": "@janedoe",
        "email": "jane.doe@example.org",
        "password" : "Password123",
        "first_name": "Jane",
        "last_name": "Doe",
        "is_superuser": True,
        "is_staff": True
    },
    {
        "username": "@charlie",
        "email": "charlie.johnson@example.org",
        "password" : "Password123",
        "first_name": "Charlie",
        "last_name": "Johnson",
        "is_superuser": False,
        "is_staff": False,
    },
]

def create_username(first_name, last_name):
    return "@" + first_name.lower() + last_name.lower() + f"{randint(1,1000)}"


def create_email(first_name, last_name):
    return first_name.lower() + "." + last_name.lower() + f"{randint(1,1000)}" + "@" + choice(["example","outlookexample","gmailexample", "yahooexample"]) + choice([".org",".com",".edu",".uk",".co"])

class Command(BaseCommand):
    """Build automation command to seed the database."""

    user_fixtures_obj = []

    team_fixture = {
    "team_name" : "Team KCL",
    "description" : "Team made for members in user fixtures",
    "unique_identifier" : "#KCL",
    }

    USER_COUNT = 100
    DEFAULT_PASSWORD = "Password123"
    TASK_COUNT = 200
    TEAM_COUNT = 50
    COMMENT_COUNT = 400
    INVITATION_COUNT = 200
    help = "Seeds the database with sample data"

    def __init__(self):
        self.faker = Faker("en_GB")

    def handle(self, *args, **options):
        if not User.objects.filter(username__in=[users_in_fixture["username"] for users_in_fixture in user_fixtures]).exists():
            for user in user_fixtures:
                    self.user_fixtures_obj.append(self.create_user(user))
            self.create_team(self.user_fixtures_obj)
        self.create_users()
        self.create_teams()
        self.create_tasks()
        self.create_invitations()
        self.create_comments()

    def create_tasks(self):
        task_count = Task.objects.count()
        while task_count < self.TASK_COUNT:
            print(f"Seeding tasks {task_count}/{self.TASK_COUNT}", end="\r")
            self.generate_task()
            task_count = Task.objects.count()
        print("Task seeding complete.      ")

    def generate_task(self):
        task_heading = self.faker.sentence()[:50]
        task_description = self.faker.text()[:160]
        teams = list(Team.objects.all())
        teams.append(None)
        team_assigned = choice(teams)
        if team_assigned:
            task_owner = choice(team_assigned.users_in_team.all())
        else:
            task_owner = choice(User.objects.all())
        creation_date = self.faker.date_time_this_month(tzinfo=pytz.UTC, before_now=True, after_now=False)
        deadline_date = self.faker.date_time_this_month(tzinfo=pytz.UTC, before_now=False, after_now=True)
        task_complete = self.faker.boolean()
        completion_time = self.faker.date_time_this_month(tzinfo=pytz.UTC)
        status = choice([choice[0] for choice in Task.STATUS_CHOICES])
        priority = choice([choice[0] for choice in Task.PRIORITY_CHOICES])

        task = Task.objects.create(
            task_heading=task_heading,
            task_description=task_description,
            team_assigned=team_assigned,
            task_owner=task_owner,
            creation_date=creation_date,
            deadline_date=deadline_date,
            task_complete=task_complete,
            completion_time=completion_time,
            status=status,
            priority=priority,
        )
        if team_assigned:
            task.user_assigned.set(choices(team_assigned.users_in_team.all(), k=randint(2, 5)))

        # Update points for the task owner
        self.update_user_points(task_owner, task)
        for assigned_user in task.user_assigned.all():
            if assigned_user.id != task_owner.id:
                self.update_user_points(assigned_user, task)

    def update_user_points(self, user, task):
        if task.status == "Completed":
            user.points += 10
            user.save()

    def create_teams(self):
        team_count = Team.objects.count()
        while team_count < self.TEAM_COUNT:
            print(f"Seeding teams {team_count}/{self.TEAM_COUNT}", end="\r")
            self.generate_team()
            team_count = Team.objects.count()
        print("Team seeding complete.      ")

    def generate_team(self):
        team_name = self.faker.word()[:50]
        description = self.faker.text()[:160]
        team_owner = choice(User.objects.all())
        unique_identifier = "#" + self.faker.unique.word() + f"{randint(1,1000)}"

        team = Team.objects.create(
            team_name=team_name,
            description=description,
            team_owner=team_owner,
            unique_identifier=unique_identifier,
        )

        team.users_in_team.set(choices(User.objects.exclude(username=team_owner.username), k=randint(2, 5)))

    def create_team(self, users):
        team_owner = choice(users)
        team = Team.objects.create(
            team_name=self.team_fixture["team_name"],
            description=self.team_fixture["description"],
            team_owner=team_owner,
            unique_identifier=self.team_fixture["unique_identifier"],
        )
        users.remove(team_owner)
        team.users_in_team.set(users)

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
        if task.team_assigned:
            commentor = choice(task.team_assigned.users_in_team.all())
        else:
            commentor = task.task_owner

        Comment.objects.create(
            task=task,
            text=text,
            Commentor=commentor,
        )

    def create_invitations(self):
        invitation_count = Invitation.objects.count()
        while invitation_count < self.INVITATION_COUNT:
            print(f"Seeding invitations {invitation_count}/{self.INVITATION_COUNT}", end="\r")
            self.generate_invitation()
            invitation_count = Invitation.objects.count()
        print("Invitation seeding complete.      ")

    def generate_invitation(self):
        team_to_join = choice(Team.objects.all())
        user_creating_invitation = choice(team_to_join.users_in_team.all())

        users = []
        for user in team_to_join.users_in_team.all():
            users.append(user.username)

        user_requesting_to_join = choice(User.objects.exclude(username=users))
        

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
        user = User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password= data["password"] if "password" in data.keys() else Command.DEFAULT_PASSWORD,
            first_name=data["first_name"],
            last_name=data["last_name"],
            is_staff=data["is_staff"],
            is_superuser=data["is_superuser"],
        )

        return user
