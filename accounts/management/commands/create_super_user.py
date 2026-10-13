import os

from django.core.management.base import BaseCommand, CommandError

from accounts.models import CustomUser


class Command(BaseCommand):
    help = "Creates a superuser from ADMIN_EMAIL / ADMIN_PASSWORD, or promotes the existing user with that email"

    def handle(self, *args, **kwargs):
        email = os.environ.get('ADMIN_EMAIL')
        password = os.environ.get('ADMIN_PASSWORD')

        if not email or not password:
            raise CommandError('ADMIN_EMAIL and ADMIN_PASSWORD must be set in your environment or .env file.')

        user = CustomUser.all_objects.filter(email__iexact=email).first()
        if user is None:
            CustomUser.objects.create_superuser(email=email, full_name='Super Admin User', password=password)
            self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))
            return

        # Existing user: grant admin rights but keep their current password.
        user.is_staff = user.is_admin = user.is_superuser = user.is_verified = user.is_active = True
        user.deleted = False
        user.status = CustomUser.ACTIVE
        user.save()
        self.stdout.write(self.style.SUCCESS('Superuser updated successfully (password unchanged).'))
