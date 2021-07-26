from django.db.models.signals import post_save
from factory import SelfAttribute, post_generation
from faker.generator import random

from hear_me_django_app.accounts.models import Account, Card, Transaction, ACCOUNT_TYPE, CURRENCIES, Company, AccountOwner
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from moneyed import Money
import factory
import factory.fuzzy as fuzzy
from django.utils.translation import gettext_lazy as _

User = get_user_model()
ACCOUNT_TYPE_NO_CREDIT_CARD = [account_type[0] for account_type in ACCOUNT_TYPE if account_type[0] not in [1, 3] ]

@factory.django.mute_signals(post_save)
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User  # Equivalent to ``model = myapp.models.User``

    # first_name = factory.Faker('name', locale='pl_PL')
    # last_name = factory.Faker('last_name', locale='pl_PL')
    name = username = factory.Faker('name', locale='pl_PL')
    email = factory.Faker('email')
    password = factory.LazyFunction(lambda: make_password('pi3.1415'))
    is_staff = True
    is_superuser = True

@factory.django.mute_signals(post_save)
class AccountOwnerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AccountOwner

    # owner = factory.SubFactory('UserFactory')
    owner = factory.SubFactory(UserFactory)

class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company
        django_get_or_create = ('name', )

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
    # private_type = factory.Iterator([True, False])
    # private_account_owner = factory.RelatedFactory(AccountOwnerFactory, factory_related_name='account')
    # corporate_account_owner = factory.RelatedFactory(CompanyFactory, factory_related_name='account')
    # corporate_account_owner = factory.List([factory.SubFactory(CompanyFactory), None])

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



def populate_user(number=1):
    UserFactory.create_batch(size=number)


def populate_accounts(quantity=1):
    PrivateAccountFactory.create_batch(size=quantity)
    CorporateAccountFactory.create_batch(size=quantity)

def populate_cards(quantity=1):
    CreditCardFactory.create_batch(size=quantity)
    PaymentCardFactory.create_batch(size=quantity)
#
# def populate_user():
#     user_list = [
#         ['root', 'root@root.com', True, True],
#         ['Marlena', 'marlena@marlena.com', False, False],
#         ['Karol', 'karol@karol.com', False, False],
#         ['Zbigniew', 'zbigniew@zbigniew.com', False, False],
#         ['Natalia', 'natalia@natalia.com', False, False],
#     ]
#
#     User.objects.bulk_create([
#         User(
#             username=user[0],
#             email=user[1],
#             is_staff=user[2],
#             is_superuser=user[3],
#             is_active=True,
#             password=make_password('Kamil100!'),
#         ) for user in user_list
#     ])
#
# def populate_accounts():

