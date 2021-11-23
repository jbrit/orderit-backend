from utilities.transaction import create_ref_code
from wallet.models import PaymentEntity, Transaction
from rest_framework import serializers
from rest_framework.exceptions import NotFound

# from utilities.constants import ErrorMessages
from orders.models import Item, Meal, Order, OrderItem
from utilities.paystack import verify_payment


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
    order = serializers.SerializerMethodField()
    total_order_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = "__all__"

    def get_paid(self, obj):
        return obj.paid

    def get_order(self, obj):
        return OrderItemSerializer(obj.orderitem_set.all(), many=True).data

    def get_total_order_price(self, obj):
        return obj.total_order_price["ordered_price__sum"]


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
        return MealSerializer(obj.meal).data


class MakeOrderSerializer(serializers.Serializer):
    meal_id = serializers.CharField()
    meal_quantity = serializers.IntegerField(default=1)
    item_id = serializers.CharField(required=False)
    item_quantity = serializers.IntegerField(default=1)

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        meal_id = validated_data.get("meal_id")
        item_quantity = validated_data.get("item_quantity")
        meal_quantity = validated_data.get("meal_quantity")
        item_id = validated_data.get("item_id")

        order_item = OrderItem()
        try:
            if meal_id:
                meal = Meal.objects.get(id=meal_id)
                order_item.meal = meal
                order_item.quantity = meal_quantity
            if item_id:
                item = Item.objects.get(id=item_id)
                order_item.item = item
                order_item.quantity = item_quantity
        except:
            raise NotFound()
        

        order = Order(user=user)
        order.save()
        
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
            source=user.wallet,
            destination=payment_entity,
            amount=order.total_order_price,
            total_amount=order.total_order_price,
            status="success",
            reference=create_ref_code(),
        )
        transaction.save()

        order.transaction = transaction
        order.save()

        order_item.order = order
        order_item.save()
        message = "Payment successful, your order has been made."
        return message, order
        
        #TODO Implement stock system
