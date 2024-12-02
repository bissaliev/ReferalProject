from random import choices
from string import ascii_lowercase, ascii_uppercase, digits


def generate_invite_code(length: int = 6) -> str:
    """Генерация инвайт-кода."""
    return "".join(
        choices(ascii_lowercase + ascii_uppercase + digits, k=length)
    )
