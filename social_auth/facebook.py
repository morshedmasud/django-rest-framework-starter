import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

GRAPH_URL = 'https://graph.facebook.com'


class Facebook:
    """
    Facebook class to fetch the user info and return it
    """

    @staticmethod
    def validate(auth_token):
        """
        Check the access token was issued for this app, then fetch the user's profile.
        Returns {'id', 'name', 'email'} or None if the token is invalid.
        """
        if not (settings.FACEBOOK_APP_ID and settings.FACEBOOK_APP_SECRET):
            logger.error("FACEBOOK_APP_ID / FACEBOOK_APP_SECRET are not configured")
            return None
        try:
            # Without this check, a token issued to any other Facebook app would be accepted.
            debug = requests.get(f'{GRAPH_URL}/debug_token', timeout=10, params={
                'input_token': auth_token,
                'access_token': f'{settings.FACEBOOK_APP_ID}|{settings.FACEBOOK_APP_SECRET}',
            }).json().get('data', {})
            if not debug.get('is_valid') or str(debug.get('app_id')) != str(settings.FACEBOOK_APP_ID):
                return None

            response = requests.get(f'{GRAPH_URL}/me', timeout=10, params={
                'fields': 'id,name,email',
                'access_token': auth_token,
            })
            response.raise_for_status()
            return response.json()
        except requests.RequestException as err:
            logger.info("Facebook token validation failed: %s", err)
            return None
