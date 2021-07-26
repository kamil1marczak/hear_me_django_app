from typing import Union, List

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models
import uuid
from djmoney.models.fields import MoneyField
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from moneyed import Money
import datetime
# from simple_history.models import HistoricalRecords

from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from auditlog.registry import auditlog

ACCOUNT_TYPE = [
    (1, _("current")),
    (2, _("saving")),
    (3, _("credit card")),
    (4, _("loan")),
    (5, _("other")),
]

TRANSACTION_TYPE = [
    (1, _("bank payment")),
    (2, _("incoming bank transfer")),
    (3, _("card payment")),
    (4, _("card return")),
    (5, _("card repayment")),
    (6, _("card withdrawal to account")),
    (7, _("card withdrawal to cash")),

]

CURRENCY_CHOICES = [('USD', 'USD $'), ('EUR', 'EUR €'), ('PLN', 'PLN zł')]
CURRENCIES = ('USD', 'EUR', "PLN")


class Account(models.Model):
    IBAN = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    account_type = models.IntegerField(choices=ACCOUNT_TYPE, default=1)
    balance = MoneyField(max_digits=14, decimal_places=2, default_currency='PLN')
    limit = MoneyField(max_digits=14, decimal_places=2, default_currency='PLN', default=None, null=True, blank=True)

    @property
    def owner_name(self):
        try:
            return f'PERSON: {self.private_account_owners.first().owner.name}'
        except AttributeError:
            pass
        try:
            return f'CORPORATE: {self.corporate_account_owner.first().name}'
        except AttributeError:
            pass


    def __str__(self):
        return f"{self.get_account_type_display()} : {self.IBAN}"



class AccountOwner(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="private_owner_of")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="private_account_owners")


class Card(models.Model):
    card_number = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    name = models.CharField(max_length=512, unique=False)
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name="account_cards")

    @property
    def owner(self):
        return self.account.owner_name

    class Meta:
        unique_together = ('name', 'account',)

    def __str__(self):
        return f"{self.account.get_account_type_display()} card: {self.name} : {self.card_number}"

    @classmethod
    def create_card(cls, name: str, limit: int = 0, currency: Union[CURRENCIES] = "PLN"):
        new_account = Account(account_type=ACCOUNT_TYPE[_("credit card")], balance=Money(limit, currency))
        new_account.save()

        card = cls(name, account=new_account)

        return card



class Company(models.Model):
    name = models.TextField(unique=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="corporate_account_owner")

    def __str__(self):
        return f"company: {self.name}"

    @classmethod
    def create_company(cls, name: str, currency: Union[CURRENCIES] = "PLN"):
        new_account = Account(account_type=ACCOUNT_TYPE[_("current")], balance=Money(0, currency))
        new_account.save()

        company = cls(name, account=new_account)

        return company


import datetime
import pytz

utc_now = pytz.utc.localize(datetime.datetime.utcnow())
pst_now = utc_now.astimezone(pytz.timezone("Europe/Warsaw"))

class Transaction(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False, auto_created=True)
    money = MoneyField(max_digits=14, decimal_places=2, default_currency='PLN')
    money_receiver = MoneyField(max_digits=14, decimal_places=2, default_currency='PLN', null=True, blank=True)
    money_sender = MoneyField(max_digits=14, decimal_places=2, default_currency='PLN', null=True, blank=True)
    account_sender_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions_sender")
    account_receiver_account = models.ForeignKey(Account, on_delete=models.CASCADE,
                                                 related_name="transactions_receiver")
    # time = models.DateTimeField(default=datetime.datetime.now)
    time = models.DateTimeField(default=timezone.now)

    @property
    def account_sender(self):
        return self.account_sender_account.owner_name

    @property
    def account_receiver(self):
        return self.account_receiver_account.owner_name


auditlog.register(Account)
