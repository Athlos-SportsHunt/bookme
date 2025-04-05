from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Order

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_host', 'is_staff')
    list_filter = ('is_host', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_host', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_host'),
        }),
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'booking', 'payment_id', 'amount', 'order_timestamp')
    list_filter = ('order_timestamp',)
    search_fields = ('user__username', 'payment_id')
    readonly_fields = ('order_timestamp',)
