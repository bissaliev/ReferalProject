from api.serializers import (
    AuthTokenSerializer,
    DummyDetailSerializer,
    ErrorResponseSerializer,
    InviteCodeSerializer,
    PhoneSerializer,
    TokenResponseSerializer,
    UserSerializer,
)
from api.utils import send_confirmation_code
from django.contrib.auth import get_user_model
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

User = get_user_model()


@extend_schema(tags=["Аутентификация"])
class PhoneAuthView(APIView):
    """Вход/регистрация по номеру телефона."""

    serializer_class = PhoneSerializer

    @extend_schema(
        operation_id="Вход или регистрация пользователя.",
        request=PhoneSerializer,
        responses={
            200: OpenApiResponse(
                response=DummyDetailSerializer,
                description="Код успешно отправлен на указанный номер телефона.",
                examples=[
                    OpenApiExample(
                        name="message",
                        value={
                            "message": "Код отправлен на номер +1234567890"
                        },
                    )
                ],
            ),
        },
        description=(
            "Пользователь указывает номер телефона на который будет "
            "отправлен код верификации."
        ),
    )
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
            {"message": f"Код отправлен на номер {phone_number}"},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["Аутентификация"])
class CodeVerificationView(APIView):
    """Представление верифицирует по номеру телефона и коду верификации."""

    serializer_class = AuthTokenSerializer

    @extend_schema(
        operation_id="Получение токена по номеру телефона и коду верификации",
        request=AuthTokenSerializer,
        responses={
            200: OpenApiResponse(
                response=TokenResponseSerializer,
                description="Успешная верификация кода. Возвращается токен пользователя.",
                examples=[
                    OpenApiExample(
                        name="token",
                        value={
                            "token": "9754d29331447ec35a23e9141c6b48ec7309d141"
                        },
                    )
                ],
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Ошибки в процессе верификации. Например, неверный код или номер телефона.",
                examples=[
                    OpenApiExample(
                        name="error 400",
                        value={"error": "Неверный код верификации."},
                    )
                ],
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Номер телефона не найден.",
                examples=[
                    OpenApiExample(
                        name="error 404",
                        value={
                            "error": "Неверный или не существующий номер телефона"
                        },
                    )
                ],
            ),
        },
        description="Вход или регистрация пользователя. Отправляет код на указанный номер телефона.",
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data.get("phone_number")
        confirmation_code = serializer.validated_data.get("confirmation_code")
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response(
                {"error": "Неверный или не существующий номер телефона."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if user.confirmation_code != confirmation_code:
            return Response(
                {"error": "Неверный код верификации."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token, _ = Token.objects.get_or_create(user=user)
        user.confirmation_code = None
        user.save(update_fields=["confirmation_code"])
        return Response({"token": token.key})


@extend_schema(tags=["Пользователи"])
@extend_schema_view(
    list=extend_schema(
        operation_id="Список пользователей",
        # description="text",
        responses={200: UserSerializer},
    ),
    retrieve=extend_schema(
        operation_id="Получение одного пользователя",
        # description="text",
        responses={200: UserSerializer},
    ),
)
class UserViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """Представление для пользователей."""

    serializer_class = UserSerializer
    queryset = User.objects.all()

    @extend_schema(operation_id="Профиль пользователя")
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

    @extend_schema(
        operation_id="Активация инвайт-кода",
        request=InviteCodeSerializer,
        responses={
            200: OpenApiResponse(
                response=DummyDetailSerializer,
                description="Инвайт-код успешно активирован.",
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description=(
                    "Ошибка активации инвайт-кода. Причина: уже активирован, "
                    "самоприглашение, или неверный код."
                ),
            ),
        },
        description="Активация инвайт-кода пользователя.",
        tags=["Активация инвайт-кода"],
    )
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
