from django.conf import settings
from django.contrib import messages
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


@login_required
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
        return redirect(request.META["HTTP_REFERER"])

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
        return redirect(request.META["HTTP_REFERER"])

    form.save(
        user=user,
        team=Team.objects.get(id=team_id),
        inviting=User.objects.get(id=inviting_id),
    )
    messages.success(
        request,
        f"Successfully invited user {username}",
    )
    return redirect(request.META["HTTP_REFERER"])


@login_required
def dashboard(request):
    tasks = Task.objects.filter(task_owner=request.user)
    all_teams = Team.objects.all

    return render(request, "dashboard.html", {"tasks": tasks, "all_teams": all_teams})


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
            form.save(user=request.user)
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
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = EditTaskForm(instance=task)

    return render(request, "edit_task.html", {"form": form, "task": task})


def show_task_details(request, task_id):
    task = Task.objects.get(id=task_id)
    return render(request, "show_task.html", {"task": task})


def update_task_status(request, task_id):
    task = Task.objects.get(id=task_id)
    if request.method == "POST":
        new_status = request.POST.get("new_status")
        if new_status == "Completed":
            task.task_complete = True
            task.completion_time = timezone.now()
        else:
            task.task_complete = False
            task.completion_time = None
        task.status = new_status
        task.save()

        return redirect("dashboard")

    return render(request, "update_task_status.html", {"task": task})


def update_complete_status(request, task_id):
    task = Task.objects.get(id=task_id)
    if request.method == "POST":
        new_status = request.POST.get("new_status")
        if new_status == "Completed" and not task.task_complete:
            task.task_complete = True
            task.completion_time = timezone.now()
        elif new_status != "Completed" and task.task_complete:
            task.task_complete = False
            task.completion_time = None
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


def high_priority_tasks(request):
    user_logged_in = request.user

    all_high_priority_tasks = Task.objects.filter(priority="High")
    high_priority_tasks = []

    for task in all_high_priority_tasks:
        if (
            user_logged_in in task.user_assigned.all()
            or user_logged_in == task.task_owner
        ):
            high_priority_tasks.append(task)

    return render(request, "high_priority_tasks.html", {"tasks": high_priority_tasks})


def medium_priority_tasks(request):
    user_logged_in = request.user

    all_medium_priority_tasks = Task.objects.filter(priority="Medium")
    medium_priority_tasks = []

    for task in all_medium_priority_tasks:
        if (
            user_logged_in in task.user_assigned.all()
            or user_logged_in == task.task_owner
        ):
            medium_priority_tasks.append(task)

    return render(
        request, "medium_priority_tasks.html", {"tasks": medium_priority_tasks}
    )


def low_priority_tasks(request):
    user_logged_in = request.user

    all_low_priority_tasks = Task.objects.filter(priority="Low")
    low_priority_tasks = []

    for task in all_low_priority_tasks:
        if (
            user_logged_in in task.user_assigned.all()
            or user_logged_in == task.task_owner
        ):
            low_priority_tasks.append(task)

    return render(request, "low_priority_tasks.html", {"tasks": low_priority_tasks})


def add_comment(request, task_id):
    if request.method == "POST":
        task = Task.objects.get(id=task_id)
        comment_text = request.POST.get("comment")
        Comment.objects.create(task=task, text=comment_text)
        return redirect(request.META["HTTP_REFERER"])
    else:
        pass
