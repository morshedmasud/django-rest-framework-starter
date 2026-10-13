import logging
import traceback

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .models import ErrorLog

logger = logging.getLogger(__name__)


class Util:
    @staticmethod
    def send_email(data):
        try:
            email = EmailMessage(
                to=[data['to_email']], subject=data['email_subject'], body=data['email_body'])
            email.send()
        except Exception:
            logger.exception("Failed to send email to %s", data.get('to_email'))


def _flatten_errors(data, prefix=''):
    """Turn DRF error data (dicts/lists of ErrorDetail) into a flat list of readable strings."""
    errors = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key in ('detail', 'non_field_errors'):
                field = prefix
            else:
                field = f"{prefix}.{key}" if prefix else key
            errors.extend(_flatten_errors(value, field))
    elif isinstance(data, list):
        for item in data:
            errors.extend(_flatten_errors(item, prefix))
    else:
        errors.append(f"{prefix}: {data}" if prefix else str(data))
    return errors


def custom_exception_handler(exc, context):
    """
    Return every error as {"message": str, "errors": [str, ...]} with the right status code.
    `services.renderers.Renderer` wraps this into the standard response envelope.
    """
    response = exception_handler(exc, context)

    if response is not None:
        errors = _flatten_errors(response.data)
        response.data = {'message': errors[0] if errors else '', 'errors': errors}
        return response

    if isinstance(exc, IntegrityError):
        message = "A record with these details already exists."
        return Response({'message': message, 'errors': [message]}, status=status.HTTP_400_BAD_REQUEST)

    # Unhandled exception: log it, and only expose details in DEBUG.
    logger.exception("Unhandled API exception", exc_info=exc)
    try:
        ErrorLog.objects.create(
            level='ERROR',
            message=str(exc),
            details=''.join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        )
    except Exception:
        logger.exception("Failed to write ErrorLog")

    message = str(exc) if settings.DEBUG else "Internal server error."
    return Response({'message': message, 'errors': [message]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
