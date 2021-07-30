from decimal import Decimal
from typing import Union, List

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models
import uuid

from djmoney.contrib.exchange.models import convert_money
from djmoney.models.fields import MoneyField
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from moneyed import Money
import datetime
# from simple_history.models import HistoricalRecords

from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import (
    SearchQuery, SearchRank, SearchVectorField, TrigramSimilarity, SearchVector
)
from django.db.models import F, Q
from djmoney.models.validators import MaxMoneyValidator, MinMoneyValidator

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


# class AccountManager(models.Manager):
#
#     def get_owner(self, queryset, name, value):
#         search_query = Q(
#             Q(search_vector=SearchQuery(value))
#         )
#         return queryset.annotate(
#             search_vector=SearchVector('private_account_owners__owner__name', 'corporate_account_owner__name', )
#         ).filter(search_query)

# def validate_poitive_balance(value):
#     if value.amount < 0:
#     # if value % 2 != 0:
#         raise ValidationError(
#             _('balance can not be negative'),
#             params={'value': value},
#         )

class Account(models.Model):
    IBAN = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    account_type = models.IntegerField(choices=ACCOUNT_TYPE, default=1)
    balance = MoneyField(max_digits=14, decimal_places=2, default_currency='PLN', validators=[
        MinMoneyValidator(Money(amount=Decimal('0.01'), currency='PLN'))
        ])
    limit = MoneyField(max_digits=14, decimal_places=2, default_currency='PLN', default=None, null=True, blank=True)

    search_vector = SearchVectorField(null=True, blank=True)

    # history = AuditlogHistoryField()

    # history = HistoricalRecords()

    # objects = AccountManager()

    class Meta:  # new
        indexes = [
            GinIndex(fields=['search_vector'], name='search_vector_index')
        ]
    # def clean(self):
    #     # Don't allow draft entries to have a pub_date.
    #     if self.balance < 0:
    #         raise ValidationError({'balance': _('Balance can not be negative')})

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



from django.utils.translation import gettext_lazy as _

class Transaction(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False, auto_created=True)
    money = MoneyField(max_digits=14, decimal_places=2, default_currency='PLN',)
    money_receiver = MoneyField(max_digits=14, decimal_places=2, default_currency=None, null=True, blank=True)
    money_sender = MoneyField(max_digits=14, decimal_places=2, default_currency=None, null=True, blank=True)
    sender_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions_sender")
    receiver_account = models.ForeignKey(Account, on_delete=models.CASCADE,
                                         related_name="transactions_receiver")
    # time = models.DateTimeField(default=datetime.datetime.now)
    time = models.DateTimeField(default=timezone.now)

    # objects = TransactionQuerySet.as_manager()

    # objects = TransactionManager()

    # def get_money_receiver(self):



    def save(self, *args, **kwargs):
        if self.id == None:
            sender_curr = self.sender_account.balance_currency
            sender_money = convert_money(self.money, sender_curr)


            self.sender_account.balance = F('balance') - sender_money

            # if self.sender_account.balance < 0:
            #
            #     return None
            #
            # else:
            self.sender_account.save()

            self.money_sender = sender_money

            receiver_curr = self.receiver_account.balance_currency
            receiver_money = convert_money(self.money, receiver_curr)
            self.receiver_account.balance = F('balance') - receiver_money
            self.receiver_account.save()

            self.money_receiver = receiver_money

            super(Transaction, self).save(*args, **kwargs)
    #
    #         receiver_curr = sender_account.balance_currency
    #         receiver_money = convert_money(money, receiver_curr)
    #
    #         receiver_account.balance = F('balance') + receiver_money
    #         receiver_account.save()
    #
    #         self.create_transaction()
    #         super().save(*args, **kwargs)

    @property
    def sender_name(self):
        return self.sender_account.owner_name

    @property
    def receiver_name(self):
        return self.receiver_account.owner_name




auditlog.register(Account)
