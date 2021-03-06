from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    name = "hear_me_django_app.accounts"
    verbose_name = _("Accounts")

    def ready(self):
        try:
            import hear_me_django_app.accounts.signals  # noqa F401
        except ImportError:
            pass
