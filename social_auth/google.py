import logging

from django.conf import settings
from google.auth.transport import requests
from google.oauth2 import id_token

logger = logging.getLogger(__name__)


class Google:
    """Google class to fetch the user info and return it"""

    @staticmethod
    def validate(auth_token):
        """
        Verify a Google ID token (signature, expiry, issuer and audience).
        Returns the token's claims, or None if it is invalid.
        """
        if not settings.GOOGLE_CLIENT_ID:
            logger.error("GOOGLE_CLIENT_ID is not configured")
            return None
        try:
            id_info = id_token.verify_oauth2_token(auth_token, requests.Request(), settings.GOOGLE_CLIENT_ID)
        except ValueError as err:
            logger.info("Invalid Google token: %s", err)
            return None
        if id_info.get('iss') not in ('accounts.google.com', 'https://accounts.google.com'):
            return None
        return id_info
