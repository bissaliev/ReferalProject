from random import randint


def generate_confirm_code() -> str:
    """Генерация кода авторизации."""
    return str(randint(1000, 9999))
