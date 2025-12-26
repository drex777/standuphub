from django.core.management.base import BaseCommand
from core.models import User, Comedian, Event, Booking
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Создаем тестовые данные'
    
    def handle(self, *args, **kwargs):
        # Очистка старых данных
        Booking.objects.all().delete()
        Event.objects.all().delete()
        Comedian.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        # Создаем комиков
        comedians = []
        comedian_names = [
            'Аркадий Бессонов', 'Лизавета Клюква', 'Феликс Гротеск', 
            'Олег Шурш', 'Анна Тихонова'
        ]
        
        for name in comedian_names:
            comedian, created = Comedian.objects.get_or_create(
                name=name,
                defaults={'bio': f'Биография комика {name}. Очень смешной человек!'}
            )
            comedians.append(comedian)
        
        self.stdout.write(f'Создано комиков: {len(comedians)}')
        
        # Создаем тестового пользователя
        user, created = User.objects.get_or_create(
            email='user@test.com',
            defaults={
                'username': 'user',
                'first_name': 'Тестовый',
                'last_name': 'Пользователь',
                'role': 'user',
                'phone': '+79991234567'
            }
        )
        if created:
            user.set_password('user123')
            user.save()
        
        # Создаем мероприятия
        events = []
        event_titles = [
            'Вечер стендапа "Открытый микрофон"',
            'Юмористическое шоу "Смех до слёз"',
            'Концерт "Чёрный юмор"',
            'Выступление "Импровизация"',
            'Вечер "Стендап для начинающих"'
        ]
        
        for i, title in enumerate(event_titles):
            event = Event.objects.create(
                title=title,
                description=f'Отличное шоу с участием лучших комиков. {title}',
                date=timezone.now().date() + timedelta(days=i+1),
                time=(19, 0, 0),
                price=500 + i*100,
                status='active'
            )
            # Добавляем случайных комиков
            event_comedians = random.sample(comedians, random.randint(2, 4))
            event.comedians.set(event_comedians)
            events.append(event)
        
        self.stdout.write(f'Создано мероприятий: {len(events)}')
        
        # Создаем тестовые бронирования
        booking_statuses = ['pending', 'confirmed', 'confirmed', 'cancelled']
        for i, event in enumerate(events[:3]):
            booking = Booking.objects.create(
                user=user,
                event=event,
                seats=random.randint(1, 4),
                booking_code=f'BK{1000 + i}',
                status=booking_statuses[i] if i < len(booking_statuses) else 'pending'
            )
        
        self.stdout.write('Созданы тестовые бронирования')
        
        self.stdout.write(
            self.style.SUCCESS('✅ Тестовые данные успешно созданы!')
        )
        self.stdout.write('Доступные пользователи:')
        self.stdout.write('- Админ: admin@test.com / ваш_пароль')
        self.stdout.write('- Обычный пользователь: user@test.com / user123')