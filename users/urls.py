from django.urls import include, path

from users.views import (
    PasswordResetAPIView,
    PasswordResetConfirmAPIView,
)

urlpatterns = [
    path(
        "password/reset/",
        PasswordResetAPIView.as_view(),
        name="password_reset",
    ),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmAPIView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "",
        include("dj_rest_auth.urls"),
    ),
]