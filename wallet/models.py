from functools import reduce

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
# from django.contrib.auth import get_user_model

from utilities.constants import TRANSACTION_TYPES
from vauth.models import User
# User = get_user_model()

# Create your models here.

class Transaction(models.Model):
    payment_type = models.CharField(max_length=2, choices=TRANSACTION_TYPES)

    source = models.ForeignKey(
        "PaymentEntity", related_name="source", on_delete=models.PROTECT, null=True
    )
    destination = models.ForeignKey(
        "PaymentEntity", related_name="destination", on_delete=models.PROTECT, null=True
    )

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    amount = models.FloatField(null=True)
    total_amount = models.FloatField(null=True)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=100)
    refunded_amount = models.FloatField(default=0.0)
    refunded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True)
    api_id = models.CharField(max_length=100, null=True, unique=True)
    
    def is_paid(self):
        if self.refunded:
            return False
        return self.status == "success"

    def is_partially_refunded(self):
        return (self.refunded_amount > 0.0) and (self.refunded_amount < self.amount)

    def is_totally_refunded(self):
        return self.refunded_amount == self.amount

class PaymentEntity(models.Model):
    metadata = models.JSONField(default=dict)
    description = models.CharField(max_length=100, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = "Payment Entities"
    
class Wallet(PaymentEntity):
    user = models.ForeignKey(User, on_delete=models.PROTECT)


    def get_outbound_transactions(self):
        """
        This methods gets the internal transactions from a wallet. These are transactions
        where the source is the wallet provided and the destination is an external payment entity.
        Args:
            wallet(Wallet): the wallet association between the account and the payment customer
        """

        all_transaction_to_wallet = Transaction.objects.filter(
            source=self,
        )
        return [
            transaction
            for transaction in all_transaction_to_wallet
        ]

    def get_inbound_transactions(self):
        
        all_transaction_to_wallet = Transaction.objects.filter(
            destination=self,
        )
        return [
            transaction
            for transaction in all_transaction_to_wallet
        ]

    def get_wallet_balance(self):
        if len(self.get_inbound_transactions()) == 0 and len(self.get_outbound_transactions()) == 0:
            return 0.0
        total_inbound_transactions = reduce(
                lambda x, y: x + y,
                [transaction.amount for transaction in self.get_inbound_transactions()],
                0
            )
        total_outbound_transactions = reduce(
                lambda x, y: x + y,
                [transaction.amount for transaction in self.get_outbound_transactions()],
                0
            )
        
        return total_inbound_transactions - total_outbound_transactions


    @property
    def balance(self):
        """
        This returns the life-time amount balance of the account in the wallet
        """
        return self.get_wallet_balance()

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance, description="Personal Wallet")