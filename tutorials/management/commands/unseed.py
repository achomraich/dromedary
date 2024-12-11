from django.core.management.base import BaseCommand, CommandError
from tutorials.models.shared import *
from tutorials.models.users import *
from tutorials.models.lessons import *
from tutorials.models.invoices import *
from tutorials.models.choices import *

class Command(BaseCommand):
    """Build automation command to unseed the database."""
    
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        """Unseed the database."""

        User.objects.filter(is_staff=False).delete()