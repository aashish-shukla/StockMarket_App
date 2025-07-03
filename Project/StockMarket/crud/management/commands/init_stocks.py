from django.core.management.base import BaseCommand
from crud.services import initialize_stocks

class Command(BaseCommand):
    help = 'Initialize the database with popular stocks from Tiingo API'
    
    def handle(self, *args, **options):
        self.stdout.write('Starting stock initialization...')
        initialize_stocks()
        self.stdout.write(
            self.style.SUCCESS('Successfully initialized stocks!')
        )