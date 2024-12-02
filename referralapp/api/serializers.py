from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.models import Referral
from users.validators import validate_invite_code, validate_phone_number

User = get_user_model()


class PhoneSerializer(serializers.Serializer):
    """Сериализатор для авторизации пользователя."""

    phone_number = serializers.CharField(
        required=True,
        help_text=(
            "Введите номер телефона длиной от 10 до 15 символов без пробелов."
        ),
        error_messages={
            "invalid": "Введите корректный номер телефона",
            "min_length": "Номер телефона должен содержать минимум 10 символов.",
            "max_length": "Номер телефона не может быть длиннее 15 символов.",
        },
        label="Номер телефона",
        validators=[validate_phone_number],
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
        label="Код верификации",
    )


class InviteCodeSerializer(serializers.Serializer):
    """Сериализатор для активации инвайт-кода."""

    invite_code = serializers.CharField(
        required=True,
        help_text="Введите 6-х значный инвайт-код.",
        label="Инвайт код",
        validators=[validate_invite_code],
    )


class ReferralSerializer(serializers.ModelSerializer):
    """
    Вложенный сериализатор для отображения номеров телефонов
    приглашенных пользователей.
    """

    phone_number = serializers.ReadOnlyField(
        source="invitee.phone_number", label="номер телефона"
    )

    class Meta:
        model = Referral
        fields = ("phone_number",)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    inviters = ReferralSerializer(
        source="invited_users",
        many=True,
        read_only=True,
        label="Приглашенные пользователи",
    )
    invite_code = serializers.ReadOnlyField(
        source="invite_code.code", label="инвайт-код пользователя"
    )
    activated_invite_code = serializers.ReadOnlyField(
        source="referral_info.activated_invite_code",
        label="Активированный инвайт-код",
    )

    class Meta:
        model = User
        fields = (
            "id",
            "phone_number",
            "email",
            "first_name",
            "last_name",
            "activated_invite_code",
            "invite_code",
            "inviters",
        )


# Сериализаторы для документации


class DummyDetailSerializer(serializers.Serializer):
    message = serializers.CharField()


class DummyDetailAndStatusSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    details = serializers.CharField()


class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()


class TokenResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
