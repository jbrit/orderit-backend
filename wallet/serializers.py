from rest_framework import serializers

from utilities.exceptions import NotFoundError
from utilities.paystack import verify_payment
from utilities.transaction import create_ref_code
from wallet.models import PaymentEntity, Transaction, Wallet

class PaymentEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentEntity
        fields = '__all__'

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
        ]

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            'payment_type',
            'source',
            'destination',
            'user',
            'amount',
            'total_amount',
            'reference',
            'status',
            'refunded_amount',
            'refunded',
            'created_at',
            'is_paid',
            'is_partially_refunded',
            'is_totally_refunded',
        ]

class PaystackCallbackSerializer(serializers.Serializer):
    reference = serializers.CharField(max_length=100)

    def create(self, validated_data):
        reference = validated_data.get('reference')
        request = self.context.get("request")
        return verify_payment(request, reference)

class WalletTransactionSerializer(serializers.Serializer):
    source_id = serializers.CharField()
    destination_id = serializers.CharField()
    amount = serializers.FloatField()

    def create(self, validated_data):
        request = self.context.get('request')
        user = 1
        source_id = validated_data.get('source_id')
        destination_id = validated_data.get('destination_id')

        try:
            source = Wallet.objects.get(id=source_id)
            destination = Wallet.objects.get(id=destination_id)
        except Wallet.DoesNotExist:
            raise NotFoundError
        amount = validated_data.get('amount')
        Transaction(
            payment_type="WW",
            source=source,
            destination=destination,
            amount=float(amount),
            total_amount=float(amount),
            user_id=user,
            reference = create_ref_code(),
            status='success'
        ).save()

        transaction = {
            "current_balance": source.balance,
            **validated_data
        }
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