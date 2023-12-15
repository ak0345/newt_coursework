from django.test import TestCase
from tasks.forms import TeamSearchForm


class TeamSearchFormTest(TestCase):
    def test_form_with_valid_data(self):
        form_data = {"search_query": "Sample Team"}
        form = TeamSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["search_query"], "Sample Team")

    def test_form_with_invalid_data(self):
        form_data = {"search_query": ""}
        form = TeamSearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["search_query"], ["This field is required."])
