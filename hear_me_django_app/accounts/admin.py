from django.contrib import admin

from hear_me_django_app.accounts.models import Account, Card, Transaction, AccountOwner, Company
from hear_me_django_app.accounts.forms import TransactionForm

# from simple_history.admin import SimpleHistoryAdmin

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

    search_fields = ('IBAN',)

# class AccountHistoryAdmin(SimpleHistoryAdmin):
#     list_display = ["id", "name", "status"]
#     history_list_display = ["status"]
#     search_fields = ['name', 'user__username']
#
# admin.site.register(Account, AccountHistoryAdmin)

@admin.register(AccountOwner)
class AccountOwnerAdmin(admin.ModelAdmin):
# class AccountOwnerAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'owner', 'account')
    list_filter = ('owner', 'account')
    # history_list_display = ["status"]
    search_fields = ('id', 'owner')
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

from django.contrib import admin

class AccountInline(admin.TabularInline):
    model = Account

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    # form = TransactionForm
    list_display = (
        'time',
        'id',
        'money_currency',
        'money',
        'money_receiver_currency',
        'money_receiver',
        'money_sender_currency',
        'money_sender',
        'sender_account',
        'receiver_account',

    )
    readonly_fields = ('id',
                       'money_receiver_currency',
                       'money_receiver',
                       'money_sender_currency',
                       'money_sender',
                       )

    # inlines = [AccountInline, ]

    # def save_model(self, request, obj, form, change):


    # def save_model(self, request, obj, form, change):
    #     if form.is_valid():
    #         transaction = form.save()
    #         user_profile = UserProfile()
    #         user_profile.user = user
    #         user_profile.save()
    #
    #     super().save_model(request, obj, form, change)
    # list_filter = (
    #     'time',
    # )
