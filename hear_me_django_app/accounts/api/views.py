from rest_framework.generics import ListAPIView

from hear_me_django_app.accounts.models import Account, Card, Transaction, AccountOwner, Company
from hear_me_django_app.accounts.api.serializers import AccountSerializer, TransactionSerializer, \
    TransactionReadSerializer
from hear_me_django_app.accounts.api.filters import AccountFilterSet, TransactionFilterSet
# from .mixins import ReadWriteSerializerMixin
# from hear_me_django_app.accounts.api.filters import AccountFilterSet
# from hear_me_django_app.accounts.actions import TransactionManager

# class AccountView(ListAPIView):
#     queryset = Account.objects.all()
#     serializer_class = AccountSerializer
#     filterset_class = AccountFilterSet
#
#     def filter_queryset(self, request):
#         return super().filter_queryset(request)[:100]


# class WineSearchWordsView(ListAPIView):
#     queryset = AccountSearchWord.objects.all()
#     serializer_class = WineSearchWordSerializer
#     filterset_class = WineSearchWordFilterSet


# from django.contrib.auth import get_user_model
# from rest_framework import status
# from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin, CreateModelMixin
# from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class AccountViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = AccountSerializer
    queryset = Account.objects.all()
    filterset_class = AccountFilterSet


class TransactionViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, CreateModelMixin, GenericViewSet,):
    serializer_class = TransactionReadSerializer
    # read_serializer_class = TransactionReadSerializer
    # write_serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    filterset_class = TransactionFilterSet

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return TransactionSerializer
        return TransactionReadSerializer
    # def retrieve( self):

    # def create(self, request):
    #
    #     t =

    # def get_queryset(self, *args, **kwargs):
    #     return self.queryset.filter(id=self.request.user.id)
    #
    # @action(detail=False, methods=["GET"])
    # def me(self, request):
    #     serializer = UserSerializer(request.user, context={"request": request})
    #     return Response(status=status.HTTP_200_OK, data=serializer.data)
