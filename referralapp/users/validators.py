import re

from django.core.exceptions import ValidationError


def validate_phone_number(value):
    """Валидатор для номера телефона."""
    if not re.match(r"^\+?\d{10,15}$", value):
        raise ValidationError(
            "Номер телефона должен содержать от 10 до 15 цифр "
            "и может начинаться с '+'."
        )
