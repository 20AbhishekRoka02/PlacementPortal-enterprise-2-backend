from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.html import strip_tags


def send_password_reset_email(user):
    """
    Sends a password reset email containing a secure
    password reset link.
    """

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    reset_url = (
        f"{settings.FRONTEND_URL}"
        f"/reset-password/{uid}/{token}"
    )

    context = {
        "user": user,
        "reset_url": reset_url,
    }

    subject = render_to_string(
        "emails/password_reset_subject.txt",
        context,
    ).strip()

    html_message = render_to_string(
        "emails/password_reset.html",
        context,
    )

    plain_message = strip_tags(html_message)

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )

        email.attach_alternative(
            html_message,
            "text/html",
        )

        email.send()
    except Exception as e:
        print("subject: ", subject)
        print("plain_message: ", plain_message)