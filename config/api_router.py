from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from hear_me_django_app.users.api.views import UserViewSet
from hear_me_django_app.accounts.api.views import AccountViewSet, TransactionViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("accounts", AccountViewSet)
router.register("transactions", TransactionViewSet)


app_name = "api"
urlpatterns = router.urls
