from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.urls", namespace="api")),
    path(
        "docs/",
        TemplateView.as_view(template_name="redoc.html"),
        name="api-docs",
    ),
]

urlpatterns += [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
]
