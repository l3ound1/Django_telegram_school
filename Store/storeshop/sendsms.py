from django.core.mail import send_mail
from django.conf import settings

def send_test_email(message,email):
    subject = '300 Баллов'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, message, email_from, recipient_list)