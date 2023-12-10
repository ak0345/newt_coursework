"""Forms for the tasks app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User
from .models import Task
from .models import Team
from .models import Invitation
from django.forms import ModelForm


class TeamSearchForm(forms.Form):
    search_query = forms.CharField(label="Search Teams", max_length=100)


class InvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = [
            "user_requesting_to_join",
            "team_to_join",
        ]

    def save(self, user, team, inviting, commit=True):
        """Create a new invitation."""
        new_invitation = Invitation(
            user_requesting_to_join=user,
            team_to_join=team,
            user_creating_invitation=inviting,
        )
        new_invitation.save()
        return new_invitation

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            username = self.cleaned_data.get("username")
            password = self.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
        return user


from django import forms
from .models import Task, Team

class TaskForm(forms.ModelForm):
    priority = forms.ChoiceField(choices=Task.PRIORITY_CHOICES)
    user_assigned = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    team_assigned = forms.ModelChoiceField(queryset=Team.objects.all(), to_field_name="unique_identifier", empty_label='None')

    class Meta:
        model = Task
        fields = [
            "task_heading",
            "task_description",
            "user_assigned",
            "team_assigned",
            "deadline_date",
            "task_complete",
            "sub_tasks"
        ]

    def save(self, user, commit=True):

        new_task = super(TaskForm, self).save(commit=False)
        new_task.task_owner = user

        new_task.save()

        new_task.user_assigned.set(self.cleaned_data["user_assigned"])

        return new_task

    def set_team_assigned_queryset(self, user):
        self.fields['team_assigned'].queryset = Team.objects.filter(team_owner=user)



class EditTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ["task_owner",  "task_complete", "completion_time", "status"]


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ["first_name", "last_name", "gravatar_url", "username", "email"]


class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(),
        validators=[
            RegexValidator(
                regex=r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$",
                message="Password must contain an uppercase character, a lowercase "
                "character and a number",
            )
        ],
    )
    password_confirmation = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput()
    )

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""

        super().clean()
        new_password = self.cleaned_data.get("new_password")
        password_confirmation = self.cleaned_data.get("password_confirmation")
        if new_password != password_confirmation:
            self.add_error(
                "password_confirmation", "Confirmation does not match password."
            )


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label="Current password", widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""

        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get("password")
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error("password", "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data["new_password"]
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        """Form options."""

        model = User
        fields = ["first_name", "last_name", "username", "email"]

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get("username"),
            first_name=self.cleaned_data.get("first_name"),
            last_name=self.cleaned_data.get("last_name"),
            email=self.cleaned_data.get("email"),
            password=self.cleaned_data.get("new_password"),
        )
        return user


class TeamCreationForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["team_name", "unique_identifier", "description"]

    def save(self, user, commit=True):
        """Create a new team or update an existing team."""
        new_team = Team(
            team_name=self.cleaned_data["team_name"],
            unique_identifier=self.cleaned_data["unique_identifier"],
            description=self.cleaned_data["description"],
            team_owner=user,
        )

        if commit:
            new_team.save()
            new_team.users_in_team.set([user.id])

        return new_team


class EditTeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["team_name", "unique_identifier", "description"]

    def save(self, user, team_instance, commit=True):
        """Update an existing team."""
        team_instance.team_name = self.cleaned_data["team_name"]
        team_instance.unique_identifier = self.cleaned_data["unique_identifier"]
        team_instance.description = self.cleaned_data["description"]

        if commit:
            team_instance.save()

        return team_instance
