from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from users.utils import generate_confirm_code, generate_invite_code
from users.validators import validate_invite_code, validate_phone_number


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
        null=True,
        verbose_name="код авторизации",
    )
    invite_code = models.CharField(
        blank=True,
        max_length=6,
        verbose_name="пригласительный код",
        validators=[validate_invite_code],
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


class Referral(models.Model):
    """Реферальная система."""

    inviter = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="invited_users",
        blank=True,
        null=True,
        verbose_name="пригласивший пользователь",
    )
    invitee = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="referral_info",
        verbose_name="приглашенный пользователь",
    )
    activated_invite_code = models.CharField(
        "активированный инвайт-код",
        max_length=6,
        blank=True,
        validators=[validate_invite_code],
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата активации"
    )

    def __str__(self):
        return f"{self.inviter} пригласил {self.invitee}"

    def save(self, *args, **kwargs):
        if self.invitee == self.inviter:
            raise ValidationError(
                "Пользователь не может пригласить самого себя."
            )
        self.activated_invite_code = self.inviter.invite_code
        super().save(*args, **kwargs)
