from django.conf import settings
from django.contrib import messages
from django.db.models import Case, Value, When
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render, HttpResponseRedirect, get_object_or_404
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tasks.helpers import login_prohibited
from .models import Task
from .models import Invitation
from .forms import TaskForm
from .forms import EditTaskForm
from .forms import EditTeamForm
from .forms import InvitationForm
from django.http import HttpResponseForbidden
from .forms import TeamCreationForm
from .forms import TeamSearchForm
from .models import Team, User
from tasks.models import User
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse
from django.forms.models import model_to_dict
from datetime import datetime
from django.utils import timezone
from .models import Comment
from django.db.models import Sum

from django.db.models import Q


def lookup_everything(request):
    if request.method == "POST":
        everythingsearched = request.POST["everythingsearched"]
        teamsfound = Team.objects.filter(unique_identifier__contains=everythingsearched)
        usersfound = User.objects.filter(username__contains=everythingsearched)
        return render(
            request,
            "everything_search.html",
            {
                "everythingsearched": everythingsearched,
                "teamsfound": teamsfound,
                "usersfound": usersfound,
            },
        )
    else:
        return render(request, "everything_search.html", {})


def lookup_team(request):
    if request.method == "POST":
        teamsearched = request.POST["teamsearched"]
        teamsfound = Team.objects.filter(unique_identifier__contains=teamsearched)
        return render(
            request,
            "team_search.html",
            {"teamsearched": teamsearched, "teamsfound": teamsfound},
        )
    else:
        return render(request, "team_search.html", {})


def notifications(request):
    mynotifications = Invitation.objects.all()
    return render(request, "notifications.html", {"mynotifications": mynotifications})


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, "home.html")


def show_team(request, team_id):
    try:
        team = Team.objects.get(id=team_id)
        # posts = Post.objects.filter(author=user)
        # following = request.user.is_following(user)
        # followable = (request.user != user)
    except ObjectDoesNotExist:
        return redirect("team_management")
    else:
        return render(request, "show_team.html", {"team": team})


@login_required
def create_invitation(request, user_id, team_id):
    form = InvitationForm(request.POST)
    # Check if invitation already exists for the current team and user

    invitations_with_team = Invitation.objects.filter(
        team_to_join=Team.objects.get(id=team_id)
    )
    for invitation in invitations_with_team:
        if invitation.user_requesting_to_join.id == user_id:
            messages.error(
                request,
                "Request already exists. Awaiting approval from team owner or current user's notifications.",
            )
        return redirect(request.META["HTTP_REFERER"])

    form.save(
        user=request.user,
        team=Team.objects.get(id=team_id),
        inviting=request.user,
    )
    messages.success(
        request,
        f"Successfully requested to join {Team.objects.filter(id=team_id)[0].team_name}, awaiting approval from {Team.objects.filter(id=team_id)[0].team_owner}",
    )
    return redirect(request.META["HTTP_REFERER"])


@login_required
def accept_invitation(request, notification_id):
    invitation = Invitation.objects.get(id=notification_id)
    team = invitation.team_to_join
    user = invitation.user_requesting_to_join
    team.users_in_team.add(user)
    # Delete invitation
    invitation.delete()
    messages.success(
        request, f"Successfully added user {user.username} into team {team.team_name}!"
    )
    return redirect("notifications")


@login_required
def reject_invitation(request, notification_id):
    invitation = Invitation.objects.get(id=notification_id)
    team = invitation.team_to_join
    user = invitation.user_requesting_to_join
    # Delete invitation
    invitation.delete()
    messages.error(
        request, f"Rejected user {user.username} from joining team {team.team_name}."
    )
    return redirect("notifications")


class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url


class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ["get", "post"]
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get("next") or ""
        return self.render()

    def post(self, request):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get("next") or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect(self.next)
        messages.add_message(
            request, messages.ERROR, "The credentials provided were invalid!"
        )
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, "log_in.html", {"form": form, "next": self.next})


def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect("home")


class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = "password.html"
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({"user": self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse("dashboard")


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


def invite_user(request, team_id, inviting_id):
    data = request.POST.dict()
    username = data.get("input_username")
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(
            request,
            "User does not exist.",
        )
        return redirect("show_team", team_id=team_id)

    form = InvitationForm()
    user = User.objects.get(username=username)

    invitations_with_team = Invitation.objects.filter(
        team_to_join=Team.objects.get(id=team_id)
    )
    for invitation in invitations_with_team:
        if invitation.user_requesting_to_join.id == user.id:
            messages.error(
                request,
                "Request already exists. Awaiting approval from team owner or user's notifications.",
            )
        return redirect("show_team", team_id=team_id)

    form.save(
        user=user,
        team=Team.objects.get(id=team_id),
        inviting=User.objects.get(id=inviting_id),
    )
    messages.success(
        request,
        f"Successfully invited user {username}",
    )
    return redirect("show_team", team_id=team_id)


@login_required
def dashboard(request):
    display_tasks_settings = request.session.get(
        "display_tasks_settings",
        {
            "show_low": True,
            "show_medium": True,
            "show_high": True,
            "show_not_started": True,
            "show_in_progress": True,
            "show_completed": True,
            "show_oldest_first": True,
            "show_low_priority_first": False,
            "show_not_started_first": False,
            "simplified_view": False,
        },
    )

    all_teams = Team.objects.all()

    tasks = Task.objects.filter(
        Q(task_owner=request.user) | Q(user_assigned=request.user)
    )
    if request.method == "POST":
        option_picked = request.POST.get("filter_tasks")
        if option_picked == "toggle_low_priority":
            display_tasks_settings["show_low"] = not display_tasks_settings["show_low"]

        if option_picked == "toggle_medium_priority":
            display_tasks_settings["show_medium"] = not display_tasks_settings[
                "show_medium"
            ]

        if option_picked == "toggle_high_priority":
            display_tasks_settings["show_high"] = not display_tasks_settings[
                "show_high"
            ]

        if option_picked == "toggle_not_started":
            display_tasks_settings["show_not_started"] = not display_tasks_settings[
                "show_not_started"
            ]

        if option_picked == "toggle_in_progress":
            display_tasks_settings["show_in_progress"] = not display_tasks_settings[
                "show_in_progress"
            ]

        if option_picked == "toggle_completed":
            display_tasks_settings["show_completed"] = not display_tasks_settings[
                "show_completed"
            ]

        if (
            option_picked == "toggle_date"
            and display_tasks_settings["show_oldest_first"] != True
        ):
            display_tasks_settings["show_oldest_first"] = True
            display_tasks_settings["show_low_priority_first"] = False
            display_tasks_settings["show_not_started_first"] = False

        if (
            option_picked == "toggle_priority"
            and display_tasks_settings["show_low_priority_first"] != True
        ):
            display_tasks_settings["show_low_priority_first"] = True
            display_tasks_settings["show_not_started_first"] = False
            display_tasks_settings["show_oldest_first"] = False

        if (
            option_picked == "toggle_status"
            and display_tasks_settings["show_not_started_first"] != True
        ):
            display_tasks_settings["show_not_started_first"] = True
            display_tasks_settings["show_low_priority_first"] = False
            display_tasks_settings["show_oldest_first"] = False

        if option_picked == "toggle_simplified":
            display_tasks_settings["simplified_view"] = not display_tasks_settings[
                "simplified_view"
            ]

    if display_tasks_settings["show_not_started_first"]:
        status_order = Case(
            When(status="Not Started", then=Value(1)),
            When(status="In Progress", then=Value(2)),
            When(status="Completed", then=Value(3)),
        )
        tasks = Task.objects.alias(status_order=status_order).order_by(
            "status_order", "status"
        )
    if display_tasks_settings["show_low_priority_first"]:
        priority_order = Case(
            When(priority="High", then=Value(3)),
            When(priority="Medium", then=Value(2)),
            When(priority="Low", then=Value(1)),
        )
        tasks = Task.objects.alias(priority_order=priority_order).order_by(
            "priority_order", "priority"
        )
    if display_tasks_settings["show_oldest_first"]:
        tasks = Task.objects.order_by("creation_date")

    if display_tasks_settings["show_low"] == False:
        tasks = tasks.exclude(priority="Low")
    if display_tasks_settings["show_medium"] == False:
        tasks = tasks.exclude(priority="Medium")
    if display_tasks_settings["show_high"] == False:
        tasks = tasks.exclude(priority="High")
    if display_tasks_settings["show_not_started"] == False:
        tasks = tasks.exclude(status="Not Started")
    if display_tasks_settings["show_in_progress"] == False:
        tasks = tasks.exclude(status="In Progress")
    if display_tasks_settings["show_completed"] == False:
        tasks = tasks.exclude(status="Completed")

    request.session["display_tasks_settings"] = display_tasks_settings

    return render(
        request,
        "dashboard.html",
        {
            "tasks": tasks,
            "all_teams": all_teams,
            "display_tasks_settings": display_tasks_settings,
        },
    )


from django.shortcuts import render, redirect
from .forms import TaskForm  # Import your TaskForm


def create_task(request):
    form = TaskForm()  # Create an instance of the form
    form.set_team_assigned_queryset(
        request.user
    )  # Filter team_assigned queryset for the current user

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.task_owner = request.user
            task.save()
            return redirect("dashboard")

    return render(request, "create_task.html", {"form": form})


def create_team(request):
    # Fetch all teams and print their values for debugging
    myteams = Team.objects.all().values()
    print(myteams)

    if request.method == "POST":
        form = TeamCreationForm(request.POST)
        if form.is_valid():
            team = form.save(user=request.user, commit=True)
            return redirect("team_management")
    else:
        form = TeamCreationForm()

    return render(request, "create_team.html", {"form": form})


def leave_team(request, user_id, team_id):
    team = Team.objects.get(id=team_id)
    user = User.objects.get(id=user_id)
    team.users_in_team.remove(user)
    messages.success(request, f"Successfully left team {team.team_name}")
    return redirect("team_management")


def team_search(request):
    myteams = (
        Team.objects.filter(team_owner_id=request.user.id)
        | Team.objects.filter(users_in_team=request.user.id)
    ).distinct()
    return render(request, "team_management.html", {"myteams": myteams})


def delete_task(request, task_id):
    task = Task.objects.get(id=task_id)
    if request.method == "POST":
        task.delete()
        return redirect("dashboard")
    return render(request, "dashboard.html", {"task": task})


def edit_task(request, task_id):
    task = Task.objects.get(id=task_id)
    if request.method == "POST":
        form = EditTaskForm(request.POST, instance=task)
        form.set_team_assigned_queryset(request.user)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = EditTaskForm(instance=task)
        form.set_team_assigned_queryset(request.user)

    return render(request, "edit_task.html", {"form": form, "task": task})


def show_task_details(request, task_id):
    task = Task.objects.get(id=task_id)
    return render(request, "show_task.html", {"task": task})


def update_task_status(request, task_id):
    task = Task.objects.get(id=task_id)

    if request.method == "POST":
        new_status = request.POST.get("new_status")
        if new_status == "Completed":
            if task.status != "Completed":
                task.status = "Completed"
                task.task_complete = True
                task.completion_time = timezone.now()

                task_owner = task.task_owner
                task_owner.points += 10
                task_owner.save()

        else:
            if task.status == "Completed":
                task.status = "In Progress"
                task.task_complete = False
                task.completion_time = None

                task_owner = task.task_owner
                if task_owner.points >= 10:
                    task_owner.points -= 10
                    task_owner.save()

        task.save()
        return redirect("dashboard")

    return render(request, "dashboard.html", {"task": task})


def edit_team(request, team_id):
    team = Team.objects.get(id=team_id)
    if team.team_owner != request.user:
        messages.error(request, "Sorry, you do not have permission to edit this team.")
        return redirect("team_management")

    if request.method == "POST":
        form = EditTeamForm(request.POST, instance=team)
        if form.is_valid():
            team.save()
            return redirect("team_management")
    else:
        form = EditTeamForm(instance=team)

    return render(request, "edit_team.html", {"form": form, "team": team})


def leave_team(request, team_id):
    team = Team.objects.get(id=team_id)

    if request.user in team.users_in_team.all():
        team.users_in_team.remove(request.user)
        messages.success(request, "You have left the team successfully.")
    else:
        messages.error(request, "You are not a member of this team.")

    return redirect("team_management")


def team_delete(request, team_id):
    team = Team.objects.get(id=team_id)
    if request.method == "POST":
        team.delete()
        return redirect("team_management")
    return render(request, "team_management.html", {"team": team})


from django.shortcuts import redirect
from django.http import HttpResponseNotFound


def add_comment(request, task_id):
    if request.method == "POST":
        try:
            task = Task.objects.get(id=task_id)
            comment_text = request.POST.get("comment")
            Comment.objects.create(task=task, text=comment_text)
            return redirect("dashboard")
        except:
            return HttpResponseNotFound("Task not found")


def show_user_information(request):
    user = request.user
    teams = Team.objects.filter(team_owner=user) | Team.objects.filter(
        users_in_team=user
    )
    team_points = {}
    for team in teams:
        users_in_team = team.users_in_team.all()
        total_points = 0

        current_user_in_team = users_in_team.count()
        index = 0
        while index < current_user_in_team:
            total_points += users_in_team[index].points
            index += 1

        team_points[team] = total_points
    return render(request, "user_info.html", {"user": user, "team_points": team_points})
