from celery import task
from django.core.mail import send_mail
from aluguel_api.settings import EMAIL_HOST_USER


@task(name='send_email_password')
def send_email_password(*args, **kwargs):
    hash = kwargs.get('hash')
    title = kwargs.get('title')
    email = kwargs.get('email')

    send_mail(
        subject=title,
        message=f'Informe o seguinte código para redefinir sua senha: {hash}',
        from_email=EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=True,
    )
