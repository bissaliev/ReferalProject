from random import choices, randint


def generate_confirm_code() -> str:
    """Генерация 4-х значного кода авторизации."""
    return str(randint(1000, 9999))


def generate_invite_code(length: int = 6) -> str:
    """Генерация инвайт-кода."""
    return "".join(choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=length))
