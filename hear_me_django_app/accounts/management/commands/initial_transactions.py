from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from ._private import populate_transactions

User = get_user_model()

class Command(BaseCommand):
    help = 'admin deployment'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Indicates the number of transactions to be created')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        populate_transactions(quantity=total)
        message = "Successfully populated database with initial transactions"

        self.stdout.write(self.style.SUCCESS(message))
