import re
from unittest import mock

from django.core import mail
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser

PASSWORD = 'Str0ng-Passw0rd!'


class BaseTestCase(APITestCase):
    def setUp(self):
        cache.clear()  # reset throttling between tests

    def make_user(self, email='user@example.com', **extra):
        return CustomUser.objects.create_user(email=email, full_name='test user', password=PASSWORD, **extra)

    def login(self, email='user@example.com', password=PASSWORD):
        return self.client.post(reverse('login'), {'email': email, 'password': password}, format='json')

    def auth(self, user):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {user.tokens()['access']}")


class RegistrationTests(BaseTestCase):
    def test_register_sends_working_verification_link(self):
        res = self.client.post(reverse('register'), {
            'email': 'New@Example.com', 'full_name': 'new user', 'password': PASSWORD}, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.content)
        self.assertTrue(res.json()['success'])
        self.assertEqual(res.json()['data']['email'], 'new@example.com')
        self.assertNotIn('password', res.json()['data'])

        self.assertEqual(len(mail.outbox), 1)
        link = re.search(r'https?://\S+', mail.outbox[0].body).group(0)
        res = self.client.get(link)
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        self.assertTrue(CustomUser.objects.get(email='new@example.com').is_verified)

    def test_register_without_full_name(self):
        res = self.client.post(reverse('register'), {'email': 'a@example.com', 'password': PASSWORD}, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.content)

    def test_register_duplicate_email_and_weak_password(self):
        self.make_user()
        res = self.client.post(reverse('register'), {'email': 'USER@example.com', 'password': PASSWORD}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(res.json()['success'])
        self.assertTrue(res.json()['errors'][0].startswith('email:'))

        res = self.client.post(reverse('register'), {'email': 'b@example.com', 'password': '123'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_verification_token(self):
        res = self.client.get(reverse('verify-email') + '?token=garbage')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(BaseTestCase):
    def test_login_refresh_logout(self):
        self.make_user()
        res = self.login()
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        tokens = res.json()['data']['tokens']

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        res = self.client.get(reverse('me'))
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        self.assertEqual(res.json()['data']['email'], 'user@example.com')

        res = self.client.post(reverse('token-refresh'), {'refresh': tokens['refresh']}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        new_refresh = res.json()['data']['refresh']

        res = self.client.post(reverse('logout'), {'refresh': new_refresh}, format='json')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT, res.content)
        res = self.client.post(reverse('token-refresh'), {'refresh': new_refresh}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_wrong_password(self):
        self.make_user()
        res = self.login(password='wrong')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res.json()['message'], 'Incorrect email or password.')

    @override_settings(REQUIRE_EMAIL_VERIFICATION=True)
    def test_unverified_user_blocked_when_required(self):
        self.make_user()
        self.assertEqual(self.login().status_code, status.HTTP_401_UNAUTHORIZED)
        CustomUser.objects.filter(email='user@example.com').update(is_verified=True)
        self.assertEqual(self.login().status_code, status.HTTP_200_OK)

    def test_login_restores_soft_deleted_user(self):
        user = self.make_user()
        user.delete()
        self.assertTrue(CustomUser.all_objects.get(id=user.id).deleted)
        self.assertEqual(self.login().status_code, status.HTTP_200_OK)
        self.assertFalse(CustomUser.all_objects.get(id=user.id).deleted)

    def test_me_requires_auth(self):
        self.assertEqual(self.client.get(reverse('me')).status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordResetTests(BaseTestCase):
    def test_full_reset_flow(self):
        self.make_user()
        res = self.client.post(reverse('request-reset-password'), {'email': 'user@example.com'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        link = re.search(r'https?://\S+', mail.outbox[0].body).group(0)
        uidb64, token = link.rstrip('/').split('/')[-2:]

        self.assertEqual(self.client.get(link).status_code, status.HTTP_200_OK)
        res = self.client.patch(reverse('password-reset-complete'), {
            'password': 'An0ther-Passw0rd!', 'uidb64': uidb64, 'token': token}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        self.assertEqual(self.login(password='An0ther-Passw0rd!').status_code, status.HTTP_200_OK)

    def test_unknown_email_gets_same_response(self):
        res = self.client.post(reverse('request-reset-password'), {'email': 'nobody@example.com'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)

    def test_bad_reset_link(self):
        res = self.client.get(reverse('password-reset-confirm', kwargs={'uidb64': 'xx', 'token': 'yy'}))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class UserPermissionTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.make_user()
        self.other = self.make_user(email='other@example.com')
        self.admin = CustomUser.objects.create_superuser(email='admin@example.com', password=PASSWORD)

    def test_user_list_is_admin_only(self):
        self.auth(self.user)
        self.assertEqual(self.client.get(reverse('all-users')).status_code, status.HTTP_403_FORBIDDEN)
        self.auth(self.admin)
        res = self.client.get(reverse('all-users'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()['data']['count'], 3)

    def test_user_can_edit_self_but_not_others(self):
        self.auth(self.user)
        res = self.client.patch(reverse('single-user', kwargs={'id': self.user.id}), {'full_name': 'Changed'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        res = self.client.patch(reverse('single-user', kwargs={'id': self.other.id}), {'full_name': 'x'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_is_soft(self):
        self.auth(self.user)
        res = self.client.delete(reverse('single-user', kwargs={'id': self.user.id}))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(CustomUser.all_objects.get(id=self.user.id).deleted)


class SocialAuthTests(BaseTestCase):
    @mock.patch('social_auth.google.Google.validate')
    def test_google_creates_then_logs_in_user(self, validate):
        validate.return_value = {'sub': '123', 'email': 'g@example.com', 'email_verified': True, 'name': 'g user'}
        for _ in range(2):
            res = self.client.post('/social-auth/google/', {'auth_token': 'tok'}, format='json')
            self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
            self.assertIn('access', res.json()['data']['tokens'])
        user = CustomUser.objects.get(email='g@example.com')
        self.assertFalse(user.has_usable_password())

    @mock.patch('social_auth.google.Google.validate', return_value=None)
    def test_google_invalid_token(self, validate):
        res = self.client.post('/social-auth/google/', {'auth_token': 'bad'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('social_auth.facebook.Facebook.validate')
    def test_provider_mismatch_rejected(self, validate):
        self.make_user(email='fb@example.com')
        validate.return_value = {'id': '9', 'email': 'fb@example.com', 'name': 'fb'}
        res = self.client.post('/social-auth/facebook/', {'auth_token': 'tok'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class SiteTests(BaseTestCase):
    def test_health_ready_and_docs(self):
        self.assertEqual(self.client.get('/health/').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/ready/').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/swagger.json').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/swagger/').status_code, status.HTTP_200_OK)

    def test_unknown_route_returns_404(self):
        self.auth(self.make_user())
        res = self.client.get(reverse('single-user', kwargs={'id': 9999}))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(res.json()['success'])

    def test_admin_pages(self):
        admin = CustomUser.objects.create_superuser(email='admin@example.com', password=PASSWORD)
        self.client.force_login(admin)
        changelist = reverse('admin:accounts_customuser_changelist')
        self.assertEqual(self.client.get(changelist + '?q=admin').status_code, 200)
        self.assertEqual(self.client.get(reverse('admin:accounts_customuser_add')).status_code, 200)
        self.assertEqual(
            self.client.get(reverse('admin:accounts_customuser_change', args=[admin.id])).status_code, 200)

        res = self.client.post(reverse('admin:accounts_customuser_add'), {
            'email': 'made@example.com', 'full_name': 'Made', 'usable_password': 'true',
            'password1': PASSWORD, 'password2': PASSWORD,
        })
        self.assertEqual(res.status_code, 302, res.content[:2000])
        self.assertEqual(self.login(email='made@example.com').status_code, status.HTTP_200_OK)
