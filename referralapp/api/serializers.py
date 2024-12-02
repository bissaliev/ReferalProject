from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.models import Referral

User = get_user_model()


class PhoneSerializer(serializers.Serializer):
    """Сериализатор для авторизации пользователя."""

    phone_number = serializers.RegexField(
        regex=r"^\+?\d{10,15}$",
        required=True,
        min_length=10,
        max_length=15,
        help_text=(
            "Введите номер телефона длиной от 10 до 15 символов без пробелов."
        ),
        error_messages={
            "invalid": "Введите корректный номер телефона",
            "min_length": "Номер телефона должен содержать минимум 10 символов.",
            "max_length": "Номер телефона не может быть длиннее 15 символов.",
        },
    )


class AuthTokenSerializer(PhoneSerializer):
    """
    Сериализатор для получения токена по номеру телефона и коду верификации.
    """

    confirmation_code = serializers.CharField(
        min_length=4,
        max_length=4,
        required=True,
        help_text="Введите 4-х значный код верификации.",
    )


class InviteCodeSerializer(serializers.Serializer):
    """Сериализатор для активации инвайт-кода."""

    invite_code = serializers.RegexField(
        regex=r"^[a-zA-Z0-9]{6}$",
        min_length=6,
        max_length=6,
        required=True,
        help_text="Введите 6-х значный инвайт-код.",
        error_messages={
            "invalid": "Введите корректный инвайт-код",
            "min_length": "Инвайт-код должен содержать 6 символов.",
            "max_length": "Инвайт-код должен содержать 6 символов.",
        },
    )


class ReferralSerializer(serializers.ModelSerializer):
    """Номера приглашенных пользователей."""

    phone_number = serializers.ReadOnlyField(source="invitee.phone_number")

    class Meta:
        model = Referral
        fields = ("phone_number",)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    inviters = ReferralSerializer(source="invited_users", many=True)
    invite_code = serializers.ReadOnlyField(source="invite_code.code")

    class Meta:
        model = User
        fields = (
            "id",
            "phone_number",
            "email",
            "first_name",
            "last_name",
            # "active_invite_code",
            "invite_code",
            "inviters",
        )


class DummyDetailSerializer(serializers.Serializer):
    message = serializers.CharField()


class DummyDetailAndStatusSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    details = serializers.CharField()


class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()


class TokenResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
