from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models

from users.utils import generate_invite_code
from users.validators import validate_invite_code, validate_phone_number


class UserManager(BaseUserManager):
    """Кастомный менеджер пользователя."""

    def create_user(self, phone_number, password, **extra_fields):
        if not phone_number:
            raise ValueError(
                "У пользователя должен быть указан номер телефона."
            )
        extra_fields.setdefault("is_active", True)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Суперпользователь должен иметь is_superuser=True."
            )
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    """Пользователи."""

    username = None
    phone_number = models.CharField(
        unique=True,
        validators=[validate_phone_number],
        verbose_name="номер телефона",
        max_length=15,
    )
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone_number


class InviteCode(models.Model):
    """Инвайт код."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="invite_code"
    )

    code = models.CharField(
        blank=True,
        max_length=6,
        unique=True,
        verbose_name="пригласительный код",
        default=generate_invite_code,
        validators=[validate_invite_code],
    )

    def __str__(self):
        return f"Пользователь {self.user} | Инвайт-код: {self.code}"


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
        """
        Проверка на самоприглашение и сохранение инвайт-кода приглашающего.
        """
        if self.invitee == self.inviter:
            raise ValidationError(
                "Пользователь не может пригласить самого себя."
            )
        self.activated_invite_code = self.inviter.invite_code.code
        super().save(*args, **kwargs)
