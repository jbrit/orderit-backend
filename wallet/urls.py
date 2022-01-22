from django.urls import path
from wallet.views import (
    WalletDetailView,
    WalletListView,
    TransactionsListView,
    PaystackCallbackView,
    PaystackCardChargeView,
    WalletTransactionView
)

app_name = "wallet"

urlpatterns = [
    path("wallets/", WalletListView.as_view(), name="wallets"),
    path("my-wallet/", WalletDetailView.as_view(), name="my_wallet"),
    path("wallet-transaction/", WalletTransactionView.as_view(), name="wallet_transaction"),
    path("transactions/", TransactionsListView.as_view(), name="transactions"),
    path("paystack-callback/", PaystackCallbackView.as_view(), name="paystack_callback"),
    path("paystack-card-charge/", PaystackCardChargeView.as_view(), name="paystack_card_charge"),

]
