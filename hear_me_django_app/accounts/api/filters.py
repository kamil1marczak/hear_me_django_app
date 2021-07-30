from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db.models import Q
from django_filters.rest_framework import CharFilter, FilterSet, ChoiceFilter

from hear_me_django_app.accounts.models import Account, Card, Transaction, AccountOwner, Company, CURRENCY_CHOICES

from django_filters import rest_framework as filters


class AccountFilterSet(filters.FilterSet):
    min_balance = filters.NumberFilter(field_name="balance", lookup_expr='gte')
    max_balance = filters.NumberFilter(field_name="balance", lookup_expr='lte')
    min_limit = filters.NumberFilter(field_name="limit", lookup_expr='gte')
    max_limit = filters.NumberFilter(field_name="limit", lookup_expr='lte')

    owner = CharFilter(method='filter_query')

    def filter_query(self, queryset, name, value):
        search_query = Q(
            Q(search_vector=SearchQuery(value))
        )
        return queryset.annotate(
            search_vector=SearchVector('private_account_owners__owner__name', 'corporate_account_owner__name', )
        ).filter(search_query)

    class Meta:
        model = Account
        # fields = ['IBAN', 'account_type', 'balance', 'limit', 'owner_name']
        fields = ['IBAN', 'account_type', 'balance', 'limit', 'private_account_owners__owner',
                  'corporate_account_owner__name']


class TransactionFilterSet(FilterSet):
    sender_name = CharFilter(method='sender_filter_query')
    receiver_name = CharFilter(method='receiver_filter_query')
    money_currency = ChoiceFilter(choices=CURRENCY_CHOICES)

    # changed
    def sender_filter_query(self, queryset, name, value):
        search_query = Q(
            Q(search_vector=SearchQuery(value))
        )
        return queryset.annotate(
            search_vector=SearchVector('sender_account__private_account_owners__owner__name',
                                       'sender_account__private_account_owners__owner__name', )
        ).filter(search_query)

    def receiver_filter_query(self, queryset, name, value):
        search_query = Q(
            Q(search_vector=SearchQuery(value))
        )
        return queryset.annotate(
            search_vector=SearchVector('receiver_account__private_account_owners__owner__name',
                                       'receiver_account__private_account_owners__owner__name', )
        ).filter(search_query)

    class Meta:
        model = Transaction
        fields = ('money', 'money_currency', 'sender_account', 'receiver_account')

#
# class AccountFilterSet(FilterSet):
#     query = CharFilter(method='filter_query')
#
#     def filter_query(self, queryset, name, value):
#         return queryset.search(value)
#
#     class Meta:
#         model = Account
#         fields = ('query', 'country', 'points',)

#
# class WineSearchWordFilterSet(FilterSet):
#     query = CharFilter(method='filter_query')
#
#     def filter_query(self, queryset, name, value):
#         return queryset.search(value)
#
#     class Meta:
#         model = WineSearchWord
#         fields = ('query',)
