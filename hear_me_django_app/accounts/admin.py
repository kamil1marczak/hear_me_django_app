from django.contrib import admin

from hear_me_django_app.accounts.models import Account, Card, Transaction, AccountOwner, Company


#
# @admin.register(Account)
# class AccountAdmin(admin.ModelAdmin):
#     # pass
#     list_display = ("IBAN", "account_type", "balance", "limit", "owner_name",)
#
# @admin.register(Card)
# class CardAdmin(admin.ModelAdmin):
#     # pass
#     list_display = ("card_number", "name", "account", )
#
# @admin.register(Transaction)
# class TransactionAdmin(admin.ModelAdmin):
#     list_display = ("id", "value", "account_sender", "account_receiver", "time",)
#     # pass

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'IBAN',
        'account_type',
        'balance_currency',
        'balance',
        'limit_currency',
        'limit',
        "owner_name"
    )


@admin.register(AccountOwner)
class AccountOwnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'account')
    list_filter = ('owner', 'account')

    autocomplete_fields = ['owner', ]

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('card_number', 'name', 'account', "owner")
    list_filter = ('account', )
    search_fields = ('name', )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'account')
    list_filter = ('account',)
    search_fields = ('name',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'value_currency',
        'value',
        'account_sender_account',
        'account_receiver_account',
        'time',
    )
    list_filter = (
        'account_sender_account',
        'account_receiver_account',
        'time',
    )
