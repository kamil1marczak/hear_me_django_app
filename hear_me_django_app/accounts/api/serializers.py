import typing

from rest_framework import serializers

from hear_me_django_app.accounts.models import Account, Card, Transaction, AccountOwner, Company, CURRENCIES, \
    CURRENCY_CHOICES
# from hear_me_django_app.accounts.actions import TransactionManager
from djmoney.contrib.django_rest_framework import MoneyField
from djmoney.money import Money
from djmoney.contrib.exchange.models import convert_money


class AccountSerializer(serializers.ModelSerializer):
    # variety = serializers.SerializerMethodField()
    # winery = serializers.SerializerMethodField()
    # description = serializers.SerializerMethodField()

    # def get_IBAN(self, obj):
    #     if hasattr(obj, 'IBAN_headline'):
    #         return getattr(obj, 'variety_headline')
    #     return getattr(obj, 'variety')
    #
    # def get_winery(self, obj):
    #     if hasattr(obj, 'winery_headline'):
    #         return getattr(obj, 'winery_headline')
    #     return getattr(obj, 'winery')
    #
    # def get_description(self, obj):
    #     if hasattr(obj, 'description_headline'):
    #         return getattr(obj, 'description_headline')
    #     return getattr(obj, 'description')

    balance = MoneyField(max_digits=10, decimal_places=2)

    class Meta:
        model = Account
        fields = ('IBAN', 'account_type', 'balance', 'limit', 'owner_name')


class TransactionSerializer(serializers.ModelSerializer):
    # sender_account = AccountSerializer(many=False, read_only=False)
    # sender_account = serializers.SerializerMethodField()
    # receiver_account = AccountSerializer(many=False, read_only=False)

    #
    money = MoneyField(max_digits=10, decimal_places=2)
    # money_currency = serializers.ChoiceField(choices=CURRENCIES, read_only=False)
    money_currency = serializers.ChoiceField(choices=CURRENCIES, read_only=False)

    # money_receiver = serializers.SerializerMethodField()
    # money_sender = serializers.SerializerMethodField()
    # money = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Transaction
        fields = (
            'id', 'money', 'money_currency', 'sender_account', 'receiver_account',)
        # read_only_fields = ('id', 'money_receiver', 'money_sender',)
        # write_only_fields = ('money_currency',)

    # def get_money_receiver(self, obj):
    #     obj.sender_account.balance.currency

    def create(self, validated_data):
        currency = validated_data.pop('money_currency')
        transaction = Transaction.objects.create(**validated_data)
        return transaction


#
class TransactionReadSerializer(serializers.ModelSerializer):
    sender_account = AccountSerializer(many=False, read_only=False)
    receiver_account = AccountSerializer(many=False, read_only=False)

    class Meta:
        model = Transaction
        fields = (
            'id', 'money', 'money_currency', 'sender_account', 'receiver_account',)
