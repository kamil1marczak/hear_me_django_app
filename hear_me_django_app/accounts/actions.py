import typing
from decimal import Decimal
from typing import Union

from djmoney.money import Money
from django.db.models import F
from hear_me_django_app.accounts.models import Account, Card, Transaction, AccountOwner, Company
from moneyed import Money
import re
from uuid import UUID
from djmoney.money import Money
from djmoney.contrib.exchange.models import convert_money

# Example TransactionManager
#     TransactionManager(1000, "PLN", '	ff95b725-f8e0-4243-a841-621dd44fb1d7', 'ff7f9888-b3cd-4e19-8717-d9fdbb439d2d')


class TransactionManager:
    def __init__(self, amount: int, currency: str, sender, receiver):
        self.currency = currency
        self.money = Money(amount=amount, currency=currency)

        self.account_sender = self.account_finder(sender)
        self.account_receiver = self.account_finder(receiver)

        self.money_sender, self.money_receiver = self.account_currencies_checker()

    def execute(self):
        self.account_operations()

    def account_currencies_checker(self):
        sender_currency = self.account_sender.balance.currency
        receiver_currency = self.account_receiver.balance.currency

        if sender_currency != self.currency:
            money_sender = self.currency_exchange(self.money, sender_currency)
        else:
            money_sender = self.money

        if receiver_currency != self.currency:
            money_receiver = self.currency_exchange(self.money, receiver_currency)
        else:
            money_receiver = self.money

        return money_sender, money_receiver

    def currency_exchange(self, money: Money, target_currency: typing.Text):
        converted_money = convert_money(money, target_currency)
        return converted_money

    def account_operations(self):
        self.account_sender.balance = F('balance') - self.money_sender
        self.account_sender.save()
        self.account_receiver.balance = F('balance') + self.money_receiver
        self.account_receiver.save()
        self.create_transaction_record()

    def create_transaction_record(self):
        transaction = Transaction(money=self.money, money_sender=self.money_sender, money_receiver=self.money_receiver,
                                  account_sender_account=self.account_sender,
                                  account_receiver_account=self.account_receiver)
        transaction.save()
        return transaction

    def account_finder(self, account_credential):
        if self._uuid_validator(account_credential):
            return Account.objects.get(IBAN=account_credential)

    @staticmethod
    def _uuid_validator(value):
        pattern = re.compile(r'^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$')
        if isinstance(value, UUID):
            return True
        try:
            pattern.match(value)
            return True
        except TypeError:
            return False
