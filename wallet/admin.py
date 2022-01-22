from django.contrib import admin

from wallet.models import Wallet, Transaction, PaymentEntity

# Register your models here.
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(PaymentEntity)
