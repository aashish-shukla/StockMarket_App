from django.core.management.base import BaseCommand
from crud.models import Stock
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create sample stocks with mock data for testing'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample stocks...')
        
        sample_stocks = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'current_price': Decimal('150.00'), 'previous_close': Decimal('148.50')},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'current_price': Decimal('2800.00'), 'previous_close': Decimal('2750.00')},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'current_price': Decimal('330.00'), 'previous_close': Decimal('325.00')},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'current_price': Decimal('3300.00'), 'previous_close': Decimal('3250.00')},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'current_price': Decimal('800.00'), 'previous_close': Decimal('790.00')},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'current_price': Decimal('350.00'), 'previous_close': Decimal('345.00')},
        ]
        
        for stock_data in sample_stocks:
            stock, created = Stock.objects.update_or_create(
                symbol=stock_data['symbol'],
                defaults=stock_data
            )
            
            if created:
                self.stdout.write(f"Created {stock.symbol} - {stock.name}")
            else:
                self.stdout.write(f"Updated {stock.symbol} - {stock.name}")
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample stocks!')
        )
