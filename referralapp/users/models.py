from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from users.utils import generate_confirm_code
from users.validators import validate_invite_code, validate_phone_number


class UserManager(BaseUserManager):
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
    confirmation_code = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name="код авторизации",
    )
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone_number

    def generate_confirmation_code(self) -> str:
        """Метод генерирует 4-х значный код подтверждения."""
        new_code = generate_confirm_code()
        self.confirmation_code = new_code
        self.save(update_fields=["confirmation_code"])
        return new_code


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
