from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CodeVerificationView, PhoneAuthView, UserViewSet

app_name = "api"

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")


urlpatterns = [
    path("", include(router.urls)),
    path("auth/phone/", PhoneAuthView.as_view(), name="phone_auth"),
    path("auth/verify/", CodeVerificationView.as_view(), name="code_verify"),
]
