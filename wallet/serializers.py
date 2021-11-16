from utilities.constants import ErrorMessages
from rest_framework import serializers

from utilities.exceptions import NotFoundError
from utilities.paystack import verify_payment
from utilities.transaction import create_ref_code
from wallet.models import PaymentEntity, Transaction, Wallet


class PaymentEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentEntity
        fields = "__all__"


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = [
            "id",
            "user",
            "balance",
            "created_at",
            "metadata",
            "description",
            "created_at",
            "amount_spent",
            "amount_received",
            "amount_sent",
        ]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "transaction_type",
            "source",
            "destination",
            "user",
            "amount",
            "total_amount",
            "reference",
            "status",
            "refunded_amount",
            "refunded",
            "created_at",
            "is_paid",
            "is_partially_refunded",
            "is_totally_refunded",
        ]


class PaystackCallbackSerializer(serializers.Serializer):
    reference = serializers.CharField(max_length=100)

    def create(self, validated_data):
        reference = validated_data.get("reference")
        request = self.context.get("request")
        return verify_payment(request, reference)


class WalletTransactionSerializer(serializers.Serializer):
    source_wallet_id = serializers.CharField()
    destination_wallet_id = serializers.CharField()
    amount = serializers.FloatField()

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        source_wallet_id = validated_data.get("source_wallet_id")
        destination_wallet_id = validated_data.get("destination_wallet_id")

        try:
            source = Wallet.objects.get(id=source_wallet_id, user=user)
            destination = Wallet.objects.get(id=destination_wallet_id)
        except Wallet.DoesNotExist:
            raise NotFoundError(ErrorMessages.WalletNotFound)
        amount = validated_data.get("amount")
        Transaction(
            transaction_type="WW",
            source=source,
            destination=destination,
            amount=float(amount),
            total_amount=float(amount),
            user=user,
            reference=create_ref_code(),
            status="success",
        ).save()

        del validated_data['amount']
        transaction = {"current_balance": source.balance, "amount_sent":amount, **validated_data}
        return transaction


class CardSerializer(serializers.Serializer):
    wallet_id = serializers.IntegerField()
    email = serializers.EmailField()
    amount = serializers.FloatField()
    cvv = serializers.CharField()
    card_number = serializers.CharField()
    expiry_month = serializers.CharField()
    expiry_year = serializers.CharField()
    pin = serializers.CharField()
