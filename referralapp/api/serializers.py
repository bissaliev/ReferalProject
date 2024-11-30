import re

from rest_framework import serializers


class PhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

    def validate_phone_number(self, value):
        if not re.match(r"^\+?\d{10,15}$", value):
            raise serializers.ValidationError(
                "Введите корректный номер телефона."
            )
        return value


class AuthTokenSerializer(PhoneSerializer):
    confirmation_code = serializers.CharField(max_length=4)
