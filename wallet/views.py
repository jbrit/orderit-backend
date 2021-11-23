from django.db.models.query_utils import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response

from utilities.paystack import charge_card
from wallet.serializers import (
    CardSerializer,
    PaystackCallbackSerializer,
    TransactionSerializer,
    WalletSerializer,
    WalletTransactionSerializer,
)

# Create your views here.
class WalletListView(ListAPIView):
    """
    List all wallets available.
    """

    serializer_class = WalletSerializer
    queryset = WalletSerializer.Meta.model.objects.all()
    permission_classes = [IsAdminUser]


class WalletDetailView(GenericAPIView):
    """
    Returns the details of the requesting user's wallet.
    """

    serializer_class = WalletSerializer
    queryset = WalletSerializer.Meta.model.objects.all()

    def get_object(self):
        return self.queryset.get(user__id=self.request.user.id)

    def get(self, request, *args, **kwargs):
        wallet = self.get_object()
        serializer = self.get_serializer(wallet)
        return Response(serializer.data)


class TransactionsListView(ListAPIView):
    """
    Lists all the transactions made by the user.
    If the user is a superuser, a list of all transactions is returned.
    """

    serializer_class = TransactionSerializer
    queryset = TransactionSerializer.Meta.model.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_superuser:
            data = TransactionSerializer(self.get_queryset(), many=True).data
            return Response(data)

        wallet = request.user.wallet_set.first()
        data = TransactionSerializer(
            TransactionSerializer.Meta.model.objects.filter(
                Q(source=wallet) or Q(destination=wallet) or Q(user=request.user)
            ),
            many=True,
        ).data
        return Response(data)


class PaystackCallbackView(APIView):
    """
    This view handles the callback from Paystack for payment verification.
    """

    serializer_class = PaystackCallbackSerializer
    queryset = None
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        message, status = serializer.save()
        return Response(data={"message": message}, status=status)


class WalletTransactionView(APIView):
    """
    This view handles the transaction of money from one wallet to another.
    """

    serializer_class = WalletTransactionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        transaction = serializer.save()
        return Response(
            data={"status": "success", "transaction": transaction},
            status=status.HTTP_200_OK,
        )


class PaystackCardChargeView(APIView):
    """
    This view handles payment from a debit card using PaystackAPI.
    """

    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        info = serializer.data
        wallet_id = info["wallet_id"]
        payload = {
            "email": info["email"],
            "amount": info["amount"],
            "card": {
                "cvv": info["cvv"],
                "number": info["card_number"],
                "expiry_month": info["expiry_month"],
                "expiry_year": info["expiry_year"],
            },
            "pin": info["pin"],
            "otp": "123456",
        }
        message, status = charge_card(payload, wallet_id)
        return Response(data={"message": message}, status=status)
