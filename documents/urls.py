from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("signup/", views.signup, name="signup"),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html"
        ),
        name="password_reset",
    ),

    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),

    path("upload/", views.upload_pdf, name="upload"),
    path("document/<int:pk>/", views.document, name="document"),
    path(
    "document/<int:pk>/share-email/",
    views.share_via_email,
    name="share_via_email",
),
    path(
        "share/<uuid:token>/",
        views.shared_document,
        name="shared_document",
    ),
    path("pdf/<int:pk>/", views.pdf_file, name="pdf_file"),
    path(
        "api/document/<int:pk>/chat/",
        views.chat,
        name="chat",
    ),
    path(
    "api/document/<int:pk>/stream-chat/",
    views.stream_chat,
    name="stream_chat"
),
]