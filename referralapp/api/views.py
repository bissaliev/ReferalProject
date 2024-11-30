from api.serializers import (
    AuthTokenSerializer,
    InviteCodeSerializer,
    PhoneSerializer,
    UserSerializer,
)
from api.utils import send_confirmation_code
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

User = get_user_model()


class PhoneAuthView(APIView):
    """Представление для запроса код верификации для авторизации."""

    serializer_class = PhoneSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data.get("phone_number")
        user, _ = User.objects.get_or_create(phone_number=phone_number)
        # генерация кода верификации
        new_code = user.generate_confirmation_code()
        # отправка кода верификации пользователю
        send_confirmation_code(phone_number, new_code)
        return Response(
            {"message": f"Код отправлен на номер {phone_number}"}, status=200
        )


class CodeVerificationView(APIView):
    """Представление верифицирует по номеру телефона и коду верификации."""

    serializer_class = AuthTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data.get("phone_number")
        confirmation_code = serializer.validated_data.get("confirmation_code")
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response(
                {"error": "Неверный или не существующий номер телефона."}
            )
        if user.confirmation_code != confirmation_code:
            return Response({"error": "Неверный код."})
        token, _ = Token.objects.get_or_create(user=user)
        user.confirmation_code = None
        user.save(update_fields=["confirmation_code"])
        return Response({"token": token.key})


class UserViewSet(ModelViewSet):
    """Представление для пользователей."""

    serializer_class = UserSerializer
    queryset = User.objects.all()

    @action(methods=["GET", "PATCH", "PUT"], detail=False)
    def me(self, request):
        """Профиль пользователя."""
        if request.method == "GET":
            serializer = self.serializer_class(request.user)
            return Response(serializer.data)
        serializer = self.serializer_class(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=["POST"], detail=False, url_path="activate-invite-code")
    def activate_invite_code(self, request):
        """Активация инвайт-кода."""
        current_user = request.user
        if current_user.inviter:
            return Response(
                {"error": "Инвайт код уже активирован"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = InviteCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invite_code = serializer.validated_data.get("invite_code")
        if invite_code == current_user.invite_code:
            return Response(
                {"error": "Вы не можете пригласить самого себя."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        inviter = User.objects.filter(invite_code=invite_code).first()
        if not inviter:
            return Response(
                {"error": "Указанный инвайт-код не существует."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        current_user.inviter = inviter
        current_user.save(update_fields=["inviter"])
        return Response({"message": "Инвайт-код успешно активирован."})
