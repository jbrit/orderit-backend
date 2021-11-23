import requests, json
from datetime import datetime
from rest_framework import status
from django.conf import settings
from wallet.models import PaymentEntity, Wallet, Transaction

PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY


def verify_payment(request, reference, transaction_type="EW"):
    wallet = Wallet.objects.get(user=request.user)

    if transactionExists(reference):

        return (
            "Transaction already exists.",
            status.HTTP_400_BAD_REQUEST
        )

    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": "Bearer " + PAYSTACK_SECRET_KEY,
    }

    response = requests.request("GET", url, headers=headers)
    if response.status_code == 200:
        r = response.json()
        print(json.dumps(r, indent=2))
        payment_entity = PaymentEntity(
            metadata=r["data"]["customer"],
            description="From Paystack Inline",
        )
        payment_entity.save()
        transaction = Transaction(
            transaction_type=transaction_type,
            source=wallet,
            destination=payment_entity,
            user=wallet.user,
            amount=r["data"]["amount"] / 100,
            total_amount=r["data"]["amount"] / 100,
            status=r["data"]["status"],
            api_id=r["data"]["id"],
            reference=r["data"]["reference"],
        )

        if r["data"]["status"] == "success":
            transaction.paid_at = datetime.fromisoformat(
                r["data"]["paid_at"][:-1] + "+00:00"
            )
            result = (
                "Payment Accepted, Your wallet has been funded.",
                status.HTTP_200_OK,
            )
        else:
            result = "Payment was abandoned", status.HTTP_200_OK, transaction
        try:
            transaction.save()
        except:
            print("Transaction already exists")
    else:
        result = (
            """
            Payment could not be proccessed at this time, 
            but don't worry we would handle it and inform you about it later
            """,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return result


def charge_card(payload, wallet_id):
    wallet = Wallet.objects.get(id=wallet_id)
    url = "https://api.paystack.co/charge"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
    }
    response = requests.request(
        "POST", url, headers=headers, data=(json.dumps(payload))
    )
    if response.status_code == 200:
        r = response.json()
        print(json.dumps(r, indent=2))

        payment_entity = PaymentEntity(
            metadata=r["data"]["customer"],
            description="From Paystack Card Charge",
        )
        payment_entity.save()

        transaction = Transaction(
            destination=wallet,
            transaction_type="EW",
            user=wallet.user,
            source=payment_entity,
            status=r["data"]["status"],
            api_id=r["data"]["id"],
            amount=r["data"]["amount"] / 100,
            total_amount=r["data"]["amount"] / 100,
            reference=r["data"]["reference"],
        )
        if r["data"]["status"] == "success":
            transaction.paid_at = datetime.fromisoformat(
                r["data"]["paid_at"][:-1] + "+00:00"
            )
            message = "Successfully funded wallet", status.HTTP_200_OK

        else:
            message = "Transaction Failed", status.HTTP_404_NOT_FOUND
        transaction.save()
        return message

def transactionExists(reference):
    transaction = Transaction.objects.filter(reference=reference)
    if transaction.exists():
        return True
    else:
        return False

#TODO Create view for verifying failed payment verifications