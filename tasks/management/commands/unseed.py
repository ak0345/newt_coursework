from django.core.management.base import BaseCommand, CommandError
from tasks.models import Task, Team, Comment, Invitation,User
from django.db.models import Q

class Command(BaseCommand):
    """Build automation command to unseed the database."""
    
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        """Unseed the database."""

        User.objects.all().filter(is_staff=False, is_superuser=False).delete()
        Task.objects.all().delete()
        Team.objects.all().filter( ~Q(unique_identifier="#KCL")).delete()
        Comment.objects.all().delete()
        Invitation.objects.all().delete()
        