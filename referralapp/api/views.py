from api.serializers import AuthTokenSerializer, PhoneSerializer
from api.utils import send_confirmation_code
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()


class PhoneAuthView(APIView):
    serializer_class = PhoneSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data.get("phone_number")
        user, _ = User.objects.get_or_create(phone_number=phone_number)
        new_code = user.generate_confirmation_code()
        send_confirmation_code(phone_number, new_code)
        return Response(
            {"message": f"Код отправлен на номер {phone_number}"}, status=200
        )


class CodeVerificationView(APIView):
    serializer_class = AuthTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data.get("phone_number")
        confirmation_code = serializer.validated_data.get("confirmation_code")
        try:
            user = User.objects.get(
                phone_number=phone_number, confirmation_code=confirmation_code
            )
        except User.DoesNotExist:
            return Response({"error": "Invalid code"})
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})
