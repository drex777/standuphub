from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Comedian, Event, Booking
from .forms import EventAdminForm, CustomUserCreationForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserCreationForm
    model = User
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('role', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {'fields': ('role', 'phone')}),
    )

@admin.register(Comedian)
class ComedianAdmin(admin.ModelAdmin):
    list_display = ('name', 'bio_short')
    search_fields = ('name',)
    
    def bio_short(self, obj):
        return obj.bio[:50] + '...' if obj.bio and len(obj.bio) > 50 else obj.bio
    bio_short.short_description = 'Биография'

class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    readonly_fields = ('booking_code', 'created_at')
    can_delete = False

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    list_display = ('title', 'date', 'time', 'price', 'status', 'comedians_list')
    list_filter = ('status', 'date')
    filter_horizontal = ('comedians',)
    inlines = [BookingInline]
    search_fields = ('title', 'description')
    
    def comedians_list(self, obj):
        return ", ".join([c.name for c in obj.comedians.all()])
    comedians_list.short_description = 'Комики'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_email', 'event_title', 'seats', 'status', 'booking_code', 'created_at')
    list_filter = ('status', 'event__date')
    search_fields = ('user__email', 'booking_code', 'event__title')
    readonly_fields = ('booking_code', 'created_at')
    list_editable = ('status',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Пользователь'
    
    def event_title(self, obj):
        return obj.event.title
    event_title.short_description = 'Мероприятие'

admin.site.register(User, CustomUserAdmin)