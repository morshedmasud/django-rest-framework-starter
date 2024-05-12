from django.core.mail import EmailMessage


class Util:
    @staticmethod
    def send_email(data):
        try:
            email = EmailMessage(to=[data['to_email']], subject=data['email_subject'], body=data['email_body'])

            email.send()
        except Exception as err:
            print(f"raised error while sending email: {err}")


