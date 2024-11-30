from django.contrib.auth.models import AbstractUser
from django.db import models
from users.utils import generate_confirm_code, generate_invite_code
from users.validators import validate_phone_number


class User(AbstractUser):
    """Пользователи."""

    phone_number = models.CharField(
        unique=True,
        validators=[validate_phone_number],
        verbose_name="номер телефона",
        max_length=15,
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        verbose_name="имя пользователя",
    )
    confirmation_code = models.CharField(
        max_length=4,
        blank=True,
        verbose_name="код авторизации",
    )
    invite_code = models.CharField(
        max_length=6, blank=True, verbose_name="пригласительный код"
    )
    inviter = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inviters",
        verbose_name="инвайтер",
    )
    REQUIRED_FIELDS = ["phone_number"]

    def __str__(self):
        return self.phone_number

    def generate_confirmation_code(self) -> str:
        """Метод генерирует 4-х значный код подтверждения."""
        new_code = generate_confirm_code()
        self.confirmation_code = new_code
        self.save(update_fields=["confirmation_code"])
        return new_code

    def _generate_invite_code(self) -> str:
        """Метод генерирует 6-х значный инвайт-код."""
        return generate_invite_code(6)

    def save(self, *args, **kwargs):
        if not self.invite_code:
            invite_code = self._generate_invite_code()
            self.invite_code = invite_code
        super().save(*args, **kwargs)
