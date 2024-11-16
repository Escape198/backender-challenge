from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from core.models import TimeStampedModel


class User(TimeStampedModel, AbstractBaseUser):
    email = models.EmailField(unique=True, db_index=True)
    is_staff = models.BooleanField(default=False, help_text="Indicates if the user has admin privileges")
    is_active = models.BooleanField(default=True, help_text="Indicates if the user account is active")
    first_name = models.CharField(max_length=255, blank=True, null=True, help_text="User's first name")
    last_name = models.CharField(max_length=255, blank=True, null=True, help_text="User's last name")

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

        indexes = [
            models.Index(fields=['is_active'], name='user_is_active_idx'),
            models.Index(fields=['is_staff'], name='user_is_staff_idx'),
        ]

    def __str__(self) -> str:
        """Returns user's full name if available, otherwise their email"""
        full_name = " ".join(filter(None, [self.first_name, self.last_name]))
        return full_name or self.email
