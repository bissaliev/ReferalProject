import os
from random import randint

from django.conf import settings
from django.core.cache import cache

# константа ключа кеша для кода подтверждения
CACHE_KEY = settings.CACHE_KEY_OF_CONFIRM_CODE


def gen_confirm_code() -> str:
    """Генерация 4-х значного кода подтверждения."""
    return str(randint(1000, 9999))


def set_cache(phone_number: str, code: str) -> None:
    """Устанавливаем код верификации в кеш."""
    # Сохраняем код на 5 минут
    cache.set(f"{CACHE_KEY}_{phone_number}", str(code), timeout=300)


def get_cache(phone_number: str) -> str:
    """Устанавливаем код верификации в кеш."""
    # Сохраняем код на 5 минут
    return cache.get(f"{CACHE_KEY}_{phone_number}")


def delete_cache(phone_number: str) -> None:
    """Удаление кода верификации из кеша."""
    cache.delete(f"{CACHE_KEY}_{phone_number}")


def verify_confirm_code(phone_number: str, code: str) -> bool:
    """Верификация кода подтверждения."""
    cache_code = get_cache(phone_number)
    if cache_code == str(code):
        # удаляем ключ верификации из кеша если коды совпадают
        delete_cache(cache_code)
        return True
    return False


def send_confirmation_code(phone_number: str) -> None:
    """Имитация отправки кода верификации."""
    BASE_DIR = settings.BASE_DIR
    directory = BASE_DIR / "auth_codes"
    # генерируем ключ верификации
    new_code = gen_confirm_code()
    # сохраняем ключ верификации в кеш
    set_cache(phone_number, new_code)
    # сохраняем ключ верификации в файле
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, f"{phone_number}.txt")
    with open(file_path, "w") as file:
        file.write(f"Ваш код подтверждения: {new_code}")
    # Возвращаем код для тестирования
    return new_code
