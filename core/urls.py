from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),
    
    # Страница мероприятия
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    
    # Бронирование
    path('event/<int:event_id>/book/', views.create_booking, name='create_booking'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    
    # Личный кабинет
    path('profile/', views.profile, name='profile'),
    
    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Админские
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/bookings/', views.admin_bookings, name='admin_bookings'),
    path('admin-panel/bookings/<int:booking_id>/status/', views.admin_change_booking_status, name='change_booking_status'),
]