from django.contrib import admin
from users.models import User
from core.log_service import log_user_creation_event


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin panel for User model with optimized display settings."""
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff')
    ordering = ('-last_login',)
    readonly_fields = ('last_login', 'password')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Information', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff')}),
        ('Important Dates', {'fields': ('last_login',)}),
    )

    def save_model(self, request, obj, form, change):
        """
        Overrides save_model to log user creation events in ClickHouse.
        """
        super().save_model(request, obj, form, change)
        if not change:
            log_user_creation_event(
                user_id=obj.id,
                event_data={
                    "email": obj.email,
                    "first_name": obj.first_name,
                    "last_name": obj.last_name,
                }
            )
