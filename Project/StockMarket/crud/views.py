from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User  # Add this import
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, F, Q
from django.core.paginator import Paginator
from .models import Stock, Portfolio, Transaction, Watchlist, UserProfile, StockNews
from .forms import BuyStockForm, SellStockForm, CustomUserCreationForm
from .services import TiingoService
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
import uuid
import json
import logging

logger = logging.getLogger(__name__)

def home(request):
    # Get top performing stocks
    top_stocks = Stock.objects.all()[:6]
    
    # Get user's portfolio summary if logged in
    portfolio_summary = None
    if request.user.is_authenticated:
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        portfolio_items = Portfolio.objects.filter(user=request.user)
        
        total_invested = sum(item.total_invested for item in portfolio_items)
        current_value = sum(item.current_value for item in portfolio_items)
        total_profit_loss = current_value - total_invested
        
        portfolio_summary = {
            'balance': user_profile.balance,
            'total_invested': total_invested,
            'current_value': current_value,
            'total_profit_loss': total_profit_loss,
            'portfolio_count': portfolio_items.count()
        }
    
    context = {
        'top_stocks': top_stocks,
        'portfolio_summary': portfolio_summary,
    }
    return render(request, 'home.html', context)

def send_verification_email(request, user, profile):
    """Send email verification to user"""
    try:
        verification_url = request.build_absolute_uri(
            reverse('crud:verify_email', kwargs={'token': profile.email_verification_token})
        )
        
        subject = 'Verify Your StockMarket Pro Account'
        html_message = render_to_string('registration/verification_email.html', {
            'user': user,
            'verification_url': verification_url,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Verification email sent to {user.email}")
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        # Don't raise the exception, just log it
        pass

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False  # Deactivate until email verification
            user.save()
            
            # Create user profile
            profile = UserProfile.objects.create(user=user)
            
            # Send verification email
            try:
                send_verification_email(request, user, profile)
                messages.success(request, f'Account created for {user.username}! Please check your email to verify your account.')
            except Exception as e:
                logger.error(f"Email sending failed: {str(e)}")
                messages.warning(request, f'Account created for {user.username}! However, we could not send the verification email. Please try to resend it.')
            
            return redirect('crud:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def verify_email(request, token):
    """Verify user email with token"""
    try:
        profile = UserProfile.objects.get(email_verification_token=token)
        if not profile.is_email_verified:
            profile.is_email_verified = True
            profile.user.is_active = True
            profile.user.save()
            profile.save()
            
            messages.success(request, 'Your email has been verified! You can now log in.')
            return redirect('crud:login')
        else:
            messages.info(request, 'Email already verified.')
            return redirect('crud:login')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Invalid verification token.')
        return redirect('crud:register')

def resend_verification(request):
    """Resend verification email"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email, is_active=False)
            profile = user.userprofile
            if not profile.is_email_verified:
                # Generate new token
                profile.email_verification_token = uuid.uuid4()
                profile.save()
                
                send_verification_email(request, user, profile)
                messages.success(request, 'Verification email sent!')
            else:
                messages.info(request, 'Email already verified.')
        except User.DoesNotExist:
            messages.error(request, 'User not found or already active.')
    
    return render(request, 'registration/resend_verification.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('crud:home')
            else:
                messages.error(request, 'Please verify your email before logging in.')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return redirect('crud:home')

def stock_list(request):
    stocks = Stock.objects.all()
    search_query = request.GET.get('search')
    
    if search_query:
        stocks = stocks.filter(
            Q(symbol__icontains=search_query) | 
            Q(name__icontains=search_query)
        )
    
    paginator = Paginator(stocks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'stocks/stock_list.html', context)

def stock_detail(request, symbol):
    stock = get_object_or_404(Stock, symbol=symbol.upper())
    
    # Get stock news
    news = StockNews.objects.filter(stock=stock)[:5]
    
    # Check if user has this stock in watchlist
    in_watchlist = False
    user_portfolio = None
    
    if request.user.is_authenticated:
        in_watchlist = Watchlist.objects.filter(user=request.user, stock=stock).exists()
        try:
            user_portfolio = Portfolio.objects.get(user=request.user, stock=stock)
        except Portfolio.DoesNotExist:
            user_portfolio = None
    
    # Get recent transactions for this stock
    recent_transactions = Transaction.objects.filter(stock=stock).order_by('-timestamp')[:10]
    
    context = {
        'stock': stock,
        'news': news,
        'in_watchlist': in_watchlist,
        'user_portfolio': user_portfolio,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'stocks/stock_detail.html', context)

@login_required
def buy_stock(request, symbol):
    stock = get_object_or_404(Stock, symbol=symbol.upper())
    user_profile = UserProfile.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = BuyStockForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            total_cost = quantity * stock.current_price
            
            if user_profile.balance >= total_cost:
                # Update user balance
                user_profile.balance -= total_cost
                user_profile.save()
                
                # Create transaction
                Transaction.objects.create(
                    user=request.user,
                    stock=stock,
                    transaction_type='BUY',
                    quantity=quantity,
                    price=stock.current_price,
                    total_amount=total_cost
                )
                
                # Update or create portfolio entry
                portfolio_item, created = Portfolio.objects.get_or_create(
                    user=request.user,
                    stock=stock,
                    defaults={
                        'quantity': quantity,
                        'average_price': stock.current_price
                    }
                )
                
                if not created:
                    # Update existing portfolio
                    total_quantity = portfolio_item.quantity + quantity
                    total_value = (portfolio_item.quantity * portfolio_item.average_price) + total_cost
                    portfolio_item.average_price = total_value / total_quantity
                    portfolio_item.quantity = total_quantity
                    portfolio_item.save()
                
                messages.success(request, f'Successfully bought {quantity} shares of {stock.symbol}!')
                return redirect('crud:portfolio')
            else:
                messages.error(request, 'Insufficient balance!')
    else:
        form = BuyStockForm()
    
    context = {
        'form': form,
        'stock': stock,
        'user_balance': user_profile.balance,
    }
    return render(request, 'stocks/buy_stock.html', context)

@login_required
def sell_stock(request, symbol):
    stock = get_object_or_404(Stock, symbol=symbol.upper())
    user_profile = UserProfile.objects.get(user=request.user)
    
    try:
        portfolio_item = Portfolio.objects.get(user=request.user, stock=stock)
    except Portfolio.DoesNotExist:
        messages.error(request, "You don't own any shares of this stock!")
        return redirect('crud:stock_detail', symbol=symbol)
    
    if request.method == 'POST':
        form = SellStockForm(request.POST, max_quantity=portfolio_item.quantity)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            total_value = quantity * stock.current_price
            
            # Update user balance
            user_profile.balance += total_value
            user_profile.save()
            
            # Create transaction
            Transaction.objects.create(
                user=request.user,
                stock=stock,
                transaction_type='SELL',
                quantity=quantity,
                price=stock.current_price,
                total_amount=total_value
            )
            
            # Update portfolio
            portfolio_item.quantity -= quantity
            if portfolio_item.quantity == 0:
                portfolio_item.delete()
            else:
                portfolio_item.save()
            
            messages.success(request, f'Successfully sold {quantity} shares of {stock.symbol}!')
            return redirect('crud:portfolio')
    else:
        form = SellStockForm(max_quantity=portfolio_item.quantity)
    
    context = {
        'form': form,
        'stock': stock,
        'portfolio_item': portfolio_item,
    }
    return render(request, 'stocks/sell_stock.html', context)

@login_required
def portfolio(request):
    portfolio_items = Portfolio.objects.filter(user=request.user).select_related('stock')
    user_profile = UserProfile.objects.get(user=request.user)
    
    total_invested = sum(item.total_invested for item in portfolio_items)
    current_value = sum(item.current_value for item in portfolio_items)
    total_profit_loss = current_value - total_invested
    
    context = {
        'portfolio_items': portfolio_items,
        'user_profile': user_profile,
        'total_invested': total_invested,
        'current_value': current_value,
        'total_profit_loss': total_profit_loss,
    }
    return render(request, 'portfolio/portfolio.html', context)

@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'portfolio/transactions.html', context)

@login_required
def watchlist(request):
    watchlist_items = Watchlist.objects.filter(user=request.user).select_related('stock')
    
    context = {
        'watchlist_items': watchlist_items,
    }
    return render(request, 'watchlist/watchlist.html', context)

@login_required
def add_to_watchlist(request, symbol):
    stock = get_object_or_404(Stock, symbol=symbol.upper())
    
    watchlist_item, created = Watchlist.objects.get_or_create(
        user=request.user,
        stock=stock
    )
    
    if created:
        messages.success(request, f'{stock.symbol} added to watchlist!')
    else:
        messages.info(request, f'{stock.symbol} is already in your watchlist!')
    
    return redirect('crud:stock_detail', symbol=symbol)

@login_required
def remove_from_watchlist(request, symbol):
    stock = get_object_or_404(Stock, symbol=symbol.upper())
    
    try:
        watchlist_item = Watchlist.objects.get(user=request.user, stock=stock)
        watchlist_item.delete()
        messages.success(request, f'{stock.symbol} removed from watchlist!')
    except Watchlist.DoesNotExist:
        messages.error(request, f'{stock.symbol} is not in your watchlist!')
    
    return redirect('crud:watchlist')

def update_stock_price(request, symbol):
    """API endpoint to update stock price using Tiingo API"""
    if request.method == 'POST':
        try:
            stock = Stock.objects.get(symbol=symbol.upper())
            tiingo_service = TiingoService()
            updated_stock = tiingo_service.update_stock_data(stock)
            
            return JsonResponse({
                'success': True,
                'symbol': updated_stock.symbol,
                'current_price': float(updated_stock.current_price),
                'price_change': float(updated_stock.price_change),
                'price_change_percent': float(updated_stock.price_change_percent),
            })
        except Stock.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Stock not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
