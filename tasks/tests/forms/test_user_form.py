from django.test import TestCase
from django.contrib.auth.models import User
from tasks.forms import UserForm

class UserFormTest(TestCase):
    def test_valid_user_form(self):
        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "gravatar_url": "https://example.com/avatar.jpg",
        }

        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_user_form_missing_fields(self):
        form_data = {}
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_user_form_invalid_email(self):
        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "invalid_email",
            "gravatar_url": "https://example.com/avatar.jpg",
        }

        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_valid_user_form_optional_gravatar(self):
        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "gravatar_url": "",
        }

        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())
