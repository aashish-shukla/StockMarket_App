import requests
from django.conf import settings
from .models import Stock, StockNews
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TiingoService:
    def __init__(self):
        self.api_token = settings.TIINGO_API_TOKEN
        self.base_url = 'https://api.tiingo.com/tiingo/daily'
        self.news_url = 'https://api.tiingo.com/tiingo/news'
        
    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Token {self.api_token}'
        }
    
    def get_stock_data(self, symbol):
        """Fetch stock data from Tiingo API"""
        try:
            # Get basic stock info
            info_url = f"{self.base_url}/{symbol}"
            response = requests.get(info_url, headers=self.get_headers())
            
            if response.status_code == 200:
                data = response.json()
                
                # Get latest prices
                prices_url = f"{self.base_url}/{symbol}/prices"
                prices_response = requests.get(prices_url, headers=self.get_headers())
                
                if prices_response.status_code == 200:
                    prices_data = prices_response.json()
                    if prices_data:
                        latest_price = prices_data[-1]
                        
                        return {
                            'symbol': data.get('ticker', symbol).upper(),
                            'name': data.get('name', ''),
                            'current_price': latest_price.get('close', 0),
                            'previous_close': latest_price.get('prevClose', 0),
                            'volume': latest_price.get('volume', 0),
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
            return None
    
    def update_stock_data(self, stock):
        """Update existing stock with latest data"""
        data = self.get_stock_data(stock.symbol)
        
        if data:
            stock.current_price = data['current_price']
            stock.previous_close = data['previous_close']
            stock.volume = data['volume']
            stock.save()
            
        return stock
    
    def get_stock_news(self, symbol, limit=10):
        """Fetch news for a specific stock"""
        try:
            url = f"{self.news_url}?tickers={symbol}&token={self.api_token}&sortBy=publishedDate&limit={limit}"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {str(e)}")
            return []
    
    def create_or_update_stock(self, symbol):
        """Create or update a stock in the database"""
        data = self.get_stock_data(symbol)
        
        if data:
            stock, created = Stock.objects.update_or_create(
                symbol=data['symbol'],
                defaults={
                    'name': data['name'],
                    'current_price': data['current_price'],
                    'previous_close': data['previous_close'],
                    'volume': data['volume'],
                }
            )
            
            # Fetch and store news
            news_data = self.get_stock_news(symbol)
            for news_item in news_data[:5]:  # Store top 5 news items
                StockNews.objects.update_or_create(
                    stock=stock,
                    url=news_item.get('url', ''),
                    defaults={
                        'title': news_item.get('title', ''),
                        'description': news_item.get('description', ''),
                        'published_date': datetime.fromisoformat(news_item.get('publishedDate', '').replace('Z', '+00:00')),
                        'source': news_item.get('source', ''),
                    }
                )
            
            return stock
        
        return None

# Popular stocks to initialize the database
POPULAR_STOCKS = [
    'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
    'AMD', 'INTC', 'CRM', 'ORCL', 'ADBE', 'PYPL', 'UBER', 'LYFT',
    'SPOT', 'TWTR', 'SNAP', 'ZM', 'SHOP', 'SQ', 'ROKU', 'DOCU'
]

def initialize_stocks():
    """Initialize database with popular stocks"""
    tiingo_service = TiingoService()
    
    for symbol in POPULAR_STOCKS:
        try:
            print(f"Processing {symbol}...")
            stock = tiingo_service.create_or_update_stock(symbol)
            if stock:
                print(f"Successfully added/updated {symbol}")
            else:
                print(f"Failed to add {symbol} - No data returned from API")
        except Exception as e:
            print(f"Error processing {symbol}: {str(e)}")