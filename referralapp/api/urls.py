from api.views import CodeVerificationView, PhoneAuthView
from django.urls import path

app_name = "api"


urlpatterns = [
    path("auth/phone/", PhoneAuthView.as_view(), name="phone_auth"),
    path("auth/verify/", CodeVerificationView.as_view(), name="code_verify"),
]
