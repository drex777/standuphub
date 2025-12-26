from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.utils import timezone
from django.contrib.auth import views as auth_views
import random
import string

from .models import Event, Booking, User
from .forms import CustomUserCreationForm
from .decorators import admin_required
from .forms import EmailAuthenticationForm

def home(request):
    # Получаем все активные мероприятия
    from django.utils import timezone
    from datetime import date
    
    events = Event.objects.filter(
        status='active',
        date__gte=timezone.now().date()  # >= сегодня
    ).order_by('date', 'time')

    past_events = Event.objects.filter(
        status='completed'
    ).order_by('-date')[:3]
    
    # ДЕБАГ: посмотрим что в БД
    print(f"Всего событий в БД: {Event.objects.count()}")
    print(f"Активных событий: {events.count()}")
    for event in events:
        print(f"  - {event.title} ({event.date})")
    
    context = {
        'events': events,
        'past_events': past_events,
    }
    return render(request, 'core/home.html', context)

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Проверяем, можно ли бронировать
    can_book = (
        event.status == 'active' and
        event.date >= timezone.now().date()
    )
    
    context = {
        'event': event,
        'can_book': can_book,
    }
    return render(request, 'core/event_detail.html', context)

def custom_login(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        
        from django.contrib.auth import authenticate
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                from django.contrib.auth import login
                login(request, user)
                
                next_page = request.GET.get('next', 'home')
                return redirect(next_page)
            else:
                messages.error(request, 'Неверный пароль')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь с таким email не найден')
    
    return render(request, 'core/login.html')

@login_required
def create_booking(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if event.status != 'active' or event.date < timezone.now().date():
        messages.error(request, 'Бронирование для этого мероприятия недоступно')
        return redirect('event_detail', event_id=event_id)
    
    if request.method == 'POST':
        seats = int(request.POST.get('seats', 1))
        
        # Генерируем уникальный код брони
        booking_code = 'BK' + ''.join(random.choices(string.digits, k=6))
        
        # Создаем бронирование
        booking = Booking.objects.create(
            user=request.user,
            event=event,
            seats=seats,
            booking_code=booking_code,
            status='pending'
        )
        
        messages.success(request, f'Бронирование создано! Ваш код: {booking_code}')
        return redirect('profile')
    
    context = {'event': event}
    return render(request, 'core/create_booking.html', context)

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status == 'pending':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Бронирование отменено')
    
    return redirect('profile')

@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'bookings': bookings,
    }
    return render(request, 'core/profile.html', context)

def register(request):
    if request.method == 'POST':
        from .forms import CustomUserCreationFormPublic
        form = CustomUserCreationFormPublic(request.POST)
        
        if form.is_valid():
            user = form.save()
            
            from django.contrib.auth import login
            login(request, user)
            
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        from .forms import CustomUserCreationFormPublic
        form = CustomUserCreationFormPublic()
    
    context = {'form': form}
    return render(request, 'core/register.html', context)

@admin_required
def admin_dashboard(request):
    from .models import User, Event, Booking
    from django.db.models import Count
    
    stats = {
        'total_users': User.objects.count(),
        'total_events': Event.objects.count(),
        'total_bookings': Booking.objects.count(),
        'pending_bookings': Booking.objects.filter(status='pending').count(),
    }
    
    # Последние бронирования
    recent_bookings = Booking.objects.select_related('user', 'event').order_by('-created_at')[:10]
    
    context = {
        'stats': stats,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'core/admin/dashboard.html', context)

@admin_required
def admin_bookings(request):
    from .models import Booking
    
    bookings = Booking.objects.select_related('user', 'event').order_by('-created_at')

    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    context = {'bookings': bookings, 'status_filter': status_filter}
    return render(request, 'core/admin/bookings.html', context)

@admin_required
def admin_change_booking_status(request, booking_id):
    from .models import Booking
    
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'confirmed', 'cancelled']:
            booking.status = new_status
            booking.save()
            messages.success(request, f'Статус бронирования #{booking_id} изменен на {new_status}')
    
    return redirect('admin_bookings')