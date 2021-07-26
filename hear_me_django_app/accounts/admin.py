from django.contrib import admin

from hear_me_django_app.accounts.models import Account, Card, Transaction, AccountOwner, Company


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'IBAN',
        'account_type',
        'balance_currency',
        'balance',
        'limit_currency',
        'limit',
        "owner_name",
    )

# class AccountHistoryAdmin(SimpleHistoryAdmin):
#     list_display = ["id", "name", "status"]
#     history_list_display = ["status"]
#     search_fields = ['name', 'user__username']
#
# admin.site.register(Account, AccountHistoryAdmin)

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
        'money_currency',
        'money',
        'money_receiver_currency',
        'money_receiver',
        'money_sender_currency',
        'money_sender',
        'account_sender_account',
        'account_receiver_account',
        'time',
    )
    list_filter = (
        'account_sender_account',
        'account_receiver_account',
        'time',
    )
