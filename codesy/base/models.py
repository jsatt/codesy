import requests

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver

from allauth.account.signals import user_signed_up


EMAIL_URL = 'https://api.github.com/user/emails'


class User(AbstractUser):
    balanced_card_href = models.CharField(max_length=100, blank=True)
    balanced_bank_account_href = models.CharField(max_length=100, blank=True)

    USERNAME_FIELD = 'username'


@receiver(user_signed_up)
def add_email_from_signup(sender, request, user, **kwargs):
    params = {'access_token': kwargs['sociallogin'].token}
    email_data = requests.get(EMAIL_URL, params=params).json()
    if email_data:
        verified_emails = [e for e in email_data if e['verified']]
        if not verified_emails:
            return None
        sorted_emails = sorted(verified_emails,
                               key=lambda e: (e['primary'], e['verified']),
                               reverse=True)
        user.email = sorted_emails[0]['email']
        user.save(update_fields=['email'])
