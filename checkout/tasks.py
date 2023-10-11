from celery import task
from django.core.mail import send_mail
from aluguel_api.settings import EMAIL_HOST_USER


@task(name='send_user_email')
def send_user_email(*args, **kwargs):
    message = kwargs.get('message')
    title = kwargs.get('title')
    email = kwargs.get('email')

    send_mail(
        subject=title,
        message=message,
        from_email=EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=True,
    )
