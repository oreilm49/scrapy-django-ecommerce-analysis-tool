from typing import List

from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_email(subject: str, message: str, to: List[str], from_addr: str = "info@specr.ie"):
    send_mail(subject, message, from_addr, to, fail_silently=False)
