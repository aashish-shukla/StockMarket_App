from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=10000.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Balance: ${self.balance}"

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=200)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    previous_close = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    market_cap = models.BigIntegerField(null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)
    pe_ratio = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"
    
    @property
    def price_change(self):
        if self.previous_close:
            return self.current_price - self.previous_close
        return 0
    
    @property
    def price_change_percent(self):
        if self.previous_close and self.previous_close > 0:
            return ((self.current_price - self.previous_close) / self.previous_close) * 100
        return 0

class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    average_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'stock')
    
    def __str__(self):
        return f"{self.user.username} - {self.stock.symbol} ({self.quantity} shares)"
    
    @property
    def current_value(self):
        return self.quantity * self.stock.current_price
    
    @property
    def total_invested(self):
        return self.quantity * self.average_price
    
    @property
    def profit_loss(self):
        return self.current_value - self.total_invested
    
    @property
    def profit_loss_percent(self):
        if self.total_invested > 0:
            return (self.profit_loss / self.total_invested) * 100
        return 0

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} {self.quantity} {self.stock.symbol}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'stock')
    
    def __str__(self):
        return f"{self.user.username} watching {self.stock.symbol}"

class StockNews(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    description = models.TextField()
    url = models.URLField()
    published_date = models.DateTimeField()
    source = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['-published_date']
    
    def __str__(self):
        return f"{self.stock.symbol} - {self.title[:50]}"
