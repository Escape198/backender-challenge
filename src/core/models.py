
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True

    def save(
        self, force_insert: bool = False, force_update: bool = False, using: str | None = None,
        update_fields: list[str] | None = None,
    ) -> None:
        """
        Overrides the save method to update the updated_at field on each save.

        Updates the 'updated_at' field to the current time before saving the object to the database.

        force_insert: If True, the object will be inserted as new (default is False).
        force_update: If True, the object will be updated (defaults to False).
        using: The database that will be used for saving (default None).
        update_fields: A list or set of fields to be updated.
        """
        self.updated_at = timezone.now()

        if update_fields is not None:
            if isinstance(update_fields, list):
                update_fields.append('updated_at')
            elif isinstance(update_fields, set):
                update_fields.add('updated_at')

        super().save(force_insert, force_update, using, update_fields)
