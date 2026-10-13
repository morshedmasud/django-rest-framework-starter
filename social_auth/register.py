from rest_framework.exceptions import AuthenticationFailed

from accounts.models import CustomUser


def register_social_user(provider, user_id, email, name):
    """Log in the user for this social account, creating it on first sign in."""
    if not email:
        raise AuthenticationFailed('Your account has no email address; email permission is required.')

    user = CustomUser.all_objects.filter(email__iexact=email).first()

    if user is None:
        user = CustomUser.objects.create_user_social(
            email=email, full_name=name, provider=provider, social_id=user_id)
    elif user.auth_provider != provider:
        raise AuthenticationFailed(detail='Please continue your login using ' + user.auth_provider)
    elif not user.is_active:
        raise AuthenticationFailed('Account disabled, contact admin.')
    elif user.deleted:
        user.restore()

    return {
        'id': user.id,
        'full_name': user.full_name,
        'email': user.email,
        'tokens': user.tokens(),
    }
