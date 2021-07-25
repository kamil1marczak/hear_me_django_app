from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from ._private import populate_user

User = get_user_model()

class Command(BaseCommand):
    help = 'admin deployment'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Indicates the number of users to be created')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        populate_user(number=total)
        obj, created = User.objects.get_or_create(name="root", password=make_password('Kamil100!'), is_superuser=True)
        message = "Successfully populated database with initial users"
        if created:
            message += f" Superuser {obj.name} ha been created"

        self.stdout.write(self.style.SUCCESS(message))
