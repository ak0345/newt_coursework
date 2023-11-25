"""Forms for the tasks app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User
from .models import Task
from .models import Team
from django.forms import ModelForm


class TeamSearchForm(forms.Form):
    search_query = forms.CharField(label="Search Teams", max_length=100)


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
    
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['task_heading', 'task_description', 'user_assigned', 'team_assigned', 'deadline_date', 'task_complete']

    def save(self, user, commit=True):
        """Create a new team."""
        new_task = Task(
            task_heading=self.cleaned_data["task_heading"],
            task_description=self.cleaned_data["task_description"],
            task_owner=user,
            team_assigned=self.cleaned_data["team_assigned"],
            deadline_date=self.cleaned_data["deadline_date"],
            task_complete=self.cleaned_data["task_complete"],
        )

        new_task.save()

        #new_task.user_assigned.set(self.cleaned_data["user_assigned"])

        return new_task

class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ["first_name", "last_name", "username", "email"]


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
        gravatar_url = user.gravatar()
        user.gravatar_url = gravatar_url
        if commit:
            user.save()
        return user


class TeamCreationForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["team_name", "unique_identifier", "description"]

    def save(self, commit=True):
        """Create a new team."""
        if not self.is_valid():
            raise ValueError("Cannot save the form. Please ensure the form is valid.")

        new_team = Team(
            team_name=self.cleaned_data["team_name"],
            unique_identifier=self.cleaned_data["unique_identifier"],
            description=self.cleaned_data["description"],
        )
        new_team.save()
        new_team.users_in_team.set([user.id])
      
        new_team.save()

        return new_team
