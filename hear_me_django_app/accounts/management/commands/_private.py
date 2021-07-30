import pprint

from django.db.models.signals import post_save
from factory import SelfAttribute, post_generation
from faker.generator import random

from hear_me_django_app.accounts.models import Account, Card, Transaction, ACCOUNT_TYPE, CURRENCIES, Company, \
    AccountOwner
from hear_me_django_app.accounts.actions import TransactionManager
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from moneyed import Money
import factory
import factory.fuzzy as fuzzy
from django.utils.translation import gettext_lazy as _

User = get_user_model()
ACCOUNT_TYPE_NO_CREDIT_CARD = [account_type[0] for account_type in ACCOUNT_TYPE if account_type[0] not in [1, 3]]


@factory.django.mute_signals(post_save)
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User  # Equivalent to ``model = myapp.models.User``

    name = username = factory.Faker('name', locale='pl_PL')
    email = factory.Faker('email')
    password = factory.LazyFunction(lambda: make_password('pi3.1415'))
    is_staff = True
    is_superuser = True


@factory.django.mute_signals(post_save)
class AccountOwnerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AccountOwner

    owner = factory.SubFactory(UserFactory)


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company
        django_get_or_create = ('name',)

    name = factory.Faker("company")


class MoneyFactory(factory.Factory):
    class Meta:
        model = Money

    amount = fuzzy.FuzzyDecimal(0, 1000000)
    currency = fuzzy.FuzzyChoice(CURRENCIES)


@factory.django.mute_signals(post_save)
class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account
        abstract = True

    IBAN = factory.Faker('uuid4')
    account_type = fuzzy.FuzzyChoice(ACCOUNT_TYPE_NO_CREDIT_CARD)
    balance = factory.SubFactory(MoneyFactory)
    limit = None


@factory.django.mute_signals(post_save)
class PrivateAccountFactory(AccountFactory):
    private_account_owner = factory.RelatedFactory(AccountOwnerFactory, factory_related_name='account')


@factory.django.mute_signals(post_save)
class CorporateAccountFactory(AccountFactory):
    corporate_account_owner = factory.RelatedFactory(CompanyFactory, factory_related_name='account')


class CardFactoryBase(factory.django.DjangoModelFactory):
    class Meta:
        model = Card
        abstract = True

    name = factory.Faker("credit_card_provider")


@factory.django.mute_signals(post_save)
class CreditCardFactory(CardFactoryBase):
    account = factory.SubFactory(PrivateAccountFactory, account_type=3, limit=SelfAttribute('balance'))


@factory.django.mute_signals(post_save)
class PaymentCardFactory(CardFactoryBase):
    account = factory.SubFactory(PrivateAccountFactory, account_type=1, limit=None)


@factory.django.mute_signals(post_save)
class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    money = factory.SubFactory(MoneyFactory)
    sender_account = factory.Iterator(Account.objects.all())
    receiver_account = factory.Iterator(Account.objects.all())

def populate_transactions(quantity=1):
    TransactionFactory.create_batch(size=quantity)

def populate_user(number=1):
    UserFactory.create_batch(size=number)


def populate_accounts(quantity=1):
    PrivateAccountFactory.create_batch(size=quantity)
    CorporateAccountFactory.create_batch(size=quantity)


def populate_cards(quantity=1):
    CreditCardFactory.create_batch(size=quantity)
    PaymentCardFactory.create_batch(size=quantity)

#
# class TransactionMassCreator:
#     def __init__(self, quantity):
#         self.ibans = list(Account.objects.values_list("IBAN", flat=True))
#         self.quantity = quantity
#         self.transactions_kwargs = list()
#
#     def create_transactions(self):
#         for _ in range(self.quantity):
#             amount = random.randint(0, 10000)
#             currency = random.choice(CURRENCIES)
#             sender, receiver = random.sample(self.ibans, 2)
#
#             self.transactions_kwargs.append(dict(amount=amount, currency=currency, sender=sender, receiver=receiver))
#
#             transaction = TransactionManager(amount, currency, sender, receiver)
#             # return sender, rec
#
#             transaction.execute()
#
# def populate_transactions(quantity=1):
#
#     transactions = TransactionMassCreator(quantity=quantity)
#     transactions.create_transactions()
