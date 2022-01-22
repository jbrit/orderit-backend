from rest_framework.exceptions import ValidationError
from utilities.constants import CANCEL_FEE_PERCENT, Actions
from rest_framework import serializers

from utilities.transaction import create_ref_code
from utilities.exceptions import BadRequestError, NotFoundError
# from utilities.constants import ErrorMessages
from utilities.paystack import verify_payment

from wallet.models import PaymentEntity, Transaction
from orders.models import Item, Meal, Order, OrderItem


class ItemSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = "__all__"

    def get_category(self, obj):
        return obj.get_category_display()


class MealSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Meal
        fields = "__all__"

    def get_category(self, obj):
        return obj.get_category_display()

    def get_items(self, obj):
        return ItemSerializer(obj.items.all(), many=True).data

    def get_total_price(self, obj):
        return obj.total_price["price__sum"]


class OrderSerializer(serializers.ModelSerializer):
    paid = serializers.SerializerMethodField()
    reference = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()
    total_order_price = serializers.SerializerMethodField()
    vendor = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = "__all__"

    def get_paid(self, obj):
        return obj.paid

    def get_reference(self, obj):
        return obj.reference

    def get_order(self, obj):
        return OrderItemSerializer(obj.orderitem_set.all(), many=True).data

    def get_total_order_price(self, obj):
        return obj.total_order_price
    
    def get_vendor(self, obj):
        if not obj.vendor:
            return None
        return obj.vendor.get_full_name()
    
    def get_status(self, obj):
        return obj.get_status_display()


class OrderItemSerializer(serializers.ModelSerializer):
    item = serializers.SerializerMethodField()
    meal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        exclude = ["order"]

    def get_item(self, obj):
        if not obj.item:
            return None
        return ItemSerializer(obj.item).data

    def get_meal(self, obj):
        if not obj.meal:
            return None
        return MealSerializer(obj.meal).data


class MakeOrderSerializer(serializers.Serializer):
    meals = serializers.CharField(required=False)
    items = serializers.CharField(required=False)
    meal_quantities = serializers.CharField(default="")
    item_quantities = serializers.CharField(default="")

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user


        item_quantities = validated_data.get("item_quantities")
        meal_quantities = validated_data.get("meal_quantities")

        items = validated_data.get("items")
        meals = validated_data.get("meals")

        items = items.split(",") if items else ""
        meals = meals.split(",") if meals else ""

        try:
            item_quantities = item_quantities.split(",") if item_quantities else ""
            meal_quantities = meal_quantities.split(",") if meal_quantities else ""

            # order_item = OrderItem()
            order = Order(user=user, status="P")
            order.save()

            if len(items) > 0:
                for item in items:
                    _item = OrderItem(item_id=int(item))
                    if _item.item.stock > 0:
                        _item.quantity = item_quantities[items.index(item)] if item_quantities else 1
                        _item.ordered_price = _item.item.price
                        _item.order = order
                        _item.save()
                        _item.item.stock -= 1
                        _item.item.save()


                    print("first")
            
            if len(meals) > 0:
                for meal in meals:
                    _item = OrderItem(meal_id=int(meal))
                    _item.quantity = meal_quantities[items.index(meal)] if meal_quantities else 1
                    _item.ordered_price = _item.meal.total_price
                    _item.order = order
                    _item.save()
        
        except:
            raise BadRequestError("Invalid data")

        payment_entity = PaymentEntity(
            metadata={
                "user_id": user.id,
                "order_id": order.id,
            },
            description="Order for {}".format(user.email),
        )
        payment_entity.save()

        transaction = Transaction(
            user=user,
            transaction_type="WO",
            source=user.wallet_set.first(),
            destination=payment_entity,
            amount=order.total_order_price,
            total_amount=order.total_order_price,
            status="success",
            reference=create_ref_code(),
        )
        transaction.save()

        order.transaction = transaction
        order.save()

        if user.wallet_set.first().balance < order.total_order_price:
            transaction.delete()
            payment_entity.delete()
            order.delete()

            raise serializers.ValidationError(
                "Insufficient balance in your wallet. Please top up your wallet"
            )

        order = OrderSerializer(order).data

        message = "Payment successful, your order has been made."
        return message, order

        # TODO Implement stock system for meals without nested loops, print order

class UpdateOrderSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()

    def create(self, validated_data):
        request = self.context.get("request")
        action = self.context.get("action")
        user = request.user

        try:
            order = Order.objects.get(id=validated_data.get("order_id"), status="P")
            if action == Actions.Cancel:

                if user.is_superuser and user != order.user:
                    order.vendor = user
                    order.status = "AR"

                else:
                    order.status ="UR"
                    payment_entity = PaymentEntity(
                        metadata={
                            "user_id": user.id,
                            "order_id": order.id,
                        },
                        description="Cancel Order for {}".format(user.email),
                    )
                    payment_entity.save()

                    transaction = Transaction(
                        user=user,
                        transaction_type="WE",
                        source=user.wallet_set.first(),
                        destination=payment_entity,
                        amount=(order.total_order_price * CANCEL_FEE_PERCENT),
                        total_amount=(order.total_order_price * CANCEL_FEE_PERCENT),
                        status="success",
                        reference=create_ref_code(),
                    )
                    transaction.save()
                    
            elif action == Actions.Serve:
                order.status = "S"
            else:
                raise ValidationError("Invalid action")
            order.save()
            return validated_data
        except:
            raise NotFoundError("Order not found")


        