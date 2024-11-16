from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from core.models import TimeStampedModel


class User(TimeStampedModel, AbstractBaseUser):
    email = models.EmailField(unique=True, db_index=True)
    is_staff = models.BooleanField(default=False, help_text="Admin access")
    is_active = models.BooleanField(default=True, help_text="Активность пользователя")
    first_name = models.CharField(max_length=255, blank=True, null=True, help_text="User activity")
    last_name = models.CharField(max_length=255, blank=True, null=True, help_text="User's last name")

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

        indexes = [
            models.Index(fields=['is_active', 'is_staff'], name='user_status_idx'),
        ]

    def __str__(self) -> str:
        if all([self.first_name, self.last_name]):
            return f'{self.first_name} {self.last_name}'

        return self.email
