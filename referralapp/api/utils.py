import os
from random import randint

from django.conf import settings
from django.core.cache import cache


def gen_confirm_code():
    """Генерация 4-х значного кода авторизации."""
    return randint(1000, 9999)


def set_cache(phone_number, code):
    cache.set(f"confirm_code_{phone_number}", str(code), timeout=300)
    print("кеш установлен")


def verify_confirm_code(phone_number, code):
    cache_code = cache.get(f"confirm_code_{phone_number}")
    print(cache_code)
    print(cache_code == str(code))
    return cache_code == str(code)


def delete_cache(phone_number):
    is_deleted = cache.delete(f"confirm_code_{phone_number}")
    print(is_deleted)


def send_confirmation_code(phone_number):
    BASE_DIR = settings.BASE_DIR
    directory = BASE_DIR / "auth_codes"
    new_code = gen_confirm_code()
    set_cache(phone_number, new_code)
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, f"{phone_number}.txt")
    with open(file_path, "w") as file:
        file.write(f"Ваш код подтверждения: {new_code}")
