from django.core.mail import send_mail
from manobseba import settings


class EmailServices:

    @staticmethod
    def email_verification(user_info):
        try:
            message_content = {
                'subject': 'Email Verification',
                'body': f"Hello {user_info['full_name']} Welcome to Manobseba Foundation. {user_info['verify_code']} please use the code to verify your email and keep your account secure. Thanks for helping us.The Manobseba Team",
                'from': settings.EMAIL_HOST_USER,
                'to': [user_info['email']]
            }

            send_mail(
                message_content['subject'],
                message_content['body'],
                message_content['from'],
                message_content['to'],
                fail_silently=False
            )
            return True
        except SystemError as err:
            return False
