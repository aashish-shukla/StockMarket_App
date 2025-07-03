from django.urls import path
from . import views

app_name = 'crud'

urlpatterns = [
    # Authentication URLs
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Stock URLs
    path('stocks/', views.stock_list, name='stock_list'),
    path('stocks/<str:symbol>/', views.stock_detail, name='stock_detail'),
    path('stocks/<str:symbol>/buy/', views.buy_stock, name='buy_stock'),
    path('stocks/<str:symbol>/sell/', views.sell_stock, name='sell_stock'),
    
    # Portfolio URLs
    path('portfolio/', views.portfolio, name='portfolio'),
    path('transactions/', views.transaction_history, name='transactions'),
    
    # Watchlist URLs
    path('watchlist/', views.watchlist, name='watchlist'),
    path('watchlist/add/<str:symbol>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('watchlist/remove/<str:symbol>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    
    # API endpoints
    path('api/update-stock/<str:symbol>/', views.update_stock_price, name='update_stock_price'),
    
    # Email verification URLs
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
]