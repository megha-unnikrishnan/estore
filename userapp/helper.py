from django.conf import settings
from django.core.mail import send_mail





def send_forget_password_mail(email, token):
    subject = "Forgot password"
    message = f'Hi, click the link to reset your password http://13.50.204.131/user/change-password/{token}/'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email, ]
    send_mail(subject, message, email_from, recipient_list)
    return True
