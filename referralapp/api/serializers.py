import re

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class PhoneSerializer(serializers.Serializer):
    """Сериализатор для авторизации пользователя."""

    phone_number = serializers.CharField(required=True)

    def validate_phone_number(self, value):
        """Валидация номера телефона."""
        if not re.match(r"^\+?\d{10,15}$", value):
            raise serializers.ValidationError(
                "Введите корректный номер телефона."
            )
        return value


class AuthTokenSerializer(PhoneSerializer):
    """
    Сериализатор для получения токена по номеру телефона и коду верификации.
    """

    confirmation_code = serializers.CharField(max_length=4, required=True)


class InviteCodeSerializer(serializers.Serializer):
    """Сериализатор для активации инвайт-кода."""

    invite_code = serializers.CharField(required=True)

    def validate_invite_code(self, value):
        """Валидация инвайт-кода."""
        if not re.match(r"^[a-zA-Z0-9]{6}$", value):
            raise serializers.ValidationError("Некорректный инвайт код")
        return value


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    inviters = serializers.SlugRelatedField(
        slug_field="phone_number", many=True, read_only=True
    )
    active_invite_code = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "phone_number",
            "username",
            "first_name",
            "last_name",
            "active_invite_code",
            "invite_code",
            "inviters",
        )

    def get_active_invite_code(self, obj):
        """Возвращает активированный инвайт-код или None."""
        return obj.inviter.invite_code if obj.inviter else None
