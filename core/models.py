from django.db import models
from django.contrib.auth.models import AbstractUser

# Пользователь
class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.email

# Комики
class Comedian(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='comedians/', blank=True, null=True)
    
    def __str__(self):
        return self.name

# Мероприятия
class Event(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активно'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    comedians = models.ManyToManyField(Comedian, related_name='events')
    date = models.DateField()
    time = models.TimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.date})"

# Бронирования
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    seats = models.PositiveIntegerField(default=1)
    booking_code = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Бронь #{self.id} - {self.user.email}"