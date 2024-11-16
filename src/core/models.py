from django.db import models
from django.utils import timezone
from typing import Optional, List


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True

    def save(
        self, force_insert: bool = False, force_update: bool = False, using: Optional[str] = None, update_fields: Optional[List[str]] = None
    ) -> None:
        """
        Переопределение метода save, чтобы обновить поле updated_at при каждом сохранении.

        Обновляет поле 'updated_at' на текущее время перед сохранением объекта в БД.

        :param force_insert: Если True, объект будет вставлен как новый (по умолчанию False).
        :param force_update: Если True, объект будет обновлен (по умолчанию False).
        :param using: База данных, которая будет использована для сохранения (по умолчанию None).
        :param update_fields: Список или множество полей, которые нужно обновить.
        """
        self.updated_at = timezone.now()

        if update_fields is not None:
            if isinstance(update_fields, list):
                update_fields.append('updated_at')
            elif isinstance(update_fields, set):
                update_fields.add('updated_at')

        super().save(force_insert, force_update, using, update_fields)
