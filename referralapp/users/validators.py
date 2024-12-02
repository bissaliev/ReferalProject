import re

from django.core.exceptions import ValidationError


def validate_phone_number(value):
    """Валидатор для номера телефона."""
    if not re.match(r"^\+?\d{10,15}$", value):
        raise ValidationError(
            "Номер телефона должен содержать от 10 до 15 цифр "
            "и может начинаться с '+'."
        )


def validate_invite_code(value: str):
    """Валидатор для инвайт-кода."""
    if len(value) != 6:
        raise ValidationError(
            "Пригласительный код должен состоять ровно из 6 символов"
        )
    if not value.isalnum():
        raise ValidationError(
            "Пригласительный код должен содержать только буквы и цифры"
        )
