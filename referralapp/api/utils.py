import os

from django.conf import settings


def send_confirmation_code(phone_number, code):
    BASE_DIR = settings.BASE_DIR
    directory = BASE_DIR / "auth_codes"
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, f"{phone_number}.txt")
    with open(file_path, "w") as file:
        file.write(f"Ваш код подтверждения: {code}")
