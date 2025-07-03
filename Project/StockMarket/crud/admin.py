from django.contrib import admin
from .models import Stock, Portfolio, Transaction, Watchlist, UserProfile, StockNews

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email']

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'current_price', 'price_change', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['symbol', 'name']
    readonly_fields = ['last_updated']

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['user', 'stock', 'quantity', 'average_price', 'current_value', 'profit_loss']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'stock__symbol']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'stock', 'transaction_type', 'quantity', 'price', 'timestamp']
    list_filter = ['transaction_type', 'timestamp']
    search_fields = ['user__username', 'stock__symbol']

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'stock', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'stock__symbol']

@admin.register(StockNews)
class StockNewsAdmin(admin.ModelAdmin):
    list_display = ['stock', 'title', 'source', 'published_date']
    list_filter = ['source', 'published_date']
    search_fields = ['title', 'stock__symbol']
