from django.core.management.base import BaseCommand
from ._private import populate_cards


class Command(BaseCommand):
    help = 'admin deployment'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Indicates the number of cards to be created')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        populate_cards(quantity=total)
        self.stdout.write(self.style.SUCCESS("Successfully populated database with initial cards"))
