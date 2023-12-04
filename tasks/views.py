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
from .models import Task, Invitation
from .forms import TaskForm
from .forms import TeamCreationForm
from .forms import TeamSearchForm, InvitationForm
from .models import Team, User
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse
from django.forms.models import model_to_dict


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


def notifications(request):
    mynotifications = Invitation.objects.all()
    return render(request, "notifications.html", {"mynotifications": mynotifications})


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
    form = InvitationForm()  # Create an instance of the form
    messages.success(
        request,
        f"Successfully requested to join {Team.objects.filter(id=team_id)[0].team_name}, awaiting approval from {Team.objects.filter(id=team_id)[0].team_owner}",
    )
    form = InvitationForm(request.POST)
    form.save(
        user=request.user,
        team=Team.objects.get(id=team_id),
        inviting=request.user,
    )
    return redirect("dashboard")

    return render(request, "create_team.html", {"form": form})


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
    form = InvitationForm()
    data = request.POST.dict()
    username = data.get("input_username")
    user = User.objects.get(username=username)
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

    return render(request, "dashboard.html", {"tasks": tasks})


def create_task(request):
    form = TaskForm()  # Create an instance of the form

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            return redirect("dashboard")

    return render(request, "create_task.html", {"form": form})


def create_team(request):
    myteams = Team.objects.all().values()
    print(myteams)
    if request.method == "POST":
        form = TeamCreationForm(request.POST)
        if form.is_valid():
            team = form.save(request.user)
            return redirect(
                "team_management"
            )  # Create a URL for team_management page to redirect.
    else:
        form = TeamCreationForm()
    return render(request, "create_team.html", {"form": form})


def team_search(request):
    myteams = Team.objects.filter(team_owner_id=request.user.id)
    return render(request, "team_management.html", {"myteams": myteams})
