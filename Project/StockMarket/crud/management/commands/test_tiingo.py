from django.core.management.base import BaseCommand
from crud.services import TiingoService
import requests

class Command(BaseCommand):
    help = 'Test Tiingo API connection'
    
    def handle(self, *args, **options):
        self.stdout.write('Testing Tiingo API connection...')
        
        service = TiingoService()
        
        # Test basic API call
        try:
            url = f"{service.base_url}/AAPL"
            response = requests.get(url, headers=service.get_headers())
            
            self.stdout.write(f"API URL: {url}")
            self.stdout.write(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.stdout.write(f"Response: {data}")
                self.stdout.write(self.style.SUCCESS('API connection successful!'))
            else:
                self.stdout.write(f"Response: {response.text}")
                self.stdout.write(self.style.ERROR('API connection failed!'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
