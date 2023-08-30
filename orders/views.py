from utilities.constants import Actions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    CreateAPIView,
)
from rest_framework.response import Response

from orders.serializers import (
    UpdateOrderSerializer,
    ItemSerializer,
    MakeOrderSerializer,
    MealSerializer,
    OrderSerializer,
)

# Create your views here.
class ItemListView(ListAPIView):
    """
    Lists all the food items available.
    """

    serializer_class = ItemSerializer
    permission_classes = []
    queryset = ItemSerializer.Meta.model.objects.all()


class ItemCreateView(CreateAPIView):
    """
    Creates an item.
    """

    serializer_class = ItemSerializer
    permission_classes = [IsAdminUser]
    queryset = ItemSerializer.Meta.model.objects.all()


class ItemRetrieveUpdateView(RetrieveUpdateAPIView):
    """
    Updates an item, especially for stock and available fields.
    """

    serializer_class = ItemSerializer
    permission_classes = [IsAdminUser]
    queryset = ItemSerializer.Meta.model.objects.all()


class MealListView(ListAPIView):
    """
    Lists all the meals available.
    Meals are made up of items available.
    """

    serializer_class = MealSerializer
    permission_classes = []
    queryset = MealSerializer.Meta.model.objects.all()


class MealCreateView(CreateAPIView):
    """
    Creates a meal.
    """

    serializer_class = MealSerializer
    permission_classes = [IsAdminUser]
    queryset = MealSerializer.Meta.model.objects.all()

class MealRetrieveUpdateView(RetrieveUpdateAPIView):
    """
    Updates a meal.
    """

    serializer_class = MealSerializer
    permission_classes = [IsAdminUser]
    queryset = MealSerializer.Meta.model.objects.all()


class OrderListView(ListAPIView):
    """
    Lists all the orders made by the requesting user.
    If the user is a superuser, a list of all orders is returned.
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = OrderSerializer.Meta.model.objects.all()

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            data = OrderSerializer(self.get_queryset(), many=True).data
            return Response(data)

        data = OrderSerializer(
            OrderSerializer.Meta.model.objects.filter(user=request.user),
            many=True,
        ).data

        order = self.kwargs.get("order")
        if order:
            data = OrderSerializer(
                OrderSerializer.Meta.model.objects.get(id=order)
            ).data
            print(order)
        return Response(data)


class OrderRetrieveView(RetrieveAPIView):
    """
    Gets a particular order made by the requesting user.
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = OrderSerializer.Meta.model.objects.all()


class MakeOrderView(GenericAPIView):
    """
    Makes an order for the requesting user.
    The user can order items or meals.
    items: [list of items] - id
    meals: [list of meals] - id
    item_quantities: [list of corresponding item_quantities]
    meal_quantities: [list of corresponding meal_quantities]
    """

    serializer_class = MakeOrderSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        message, order = serializer.save()
        return Response(
            data={"message": message, "order": order}, status=status.HTTP_200_OK
        )


class CancelOrderView(GenericAPIView):
    """
    This view cancels any given order. For both admin, staff and customers.
    If endpoint is called by a user,
    a cancel fee of 20%of the order's price is deducted from the user's wallet
    """

    serializer_class = UpdateOrderSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request, "action": Actions.Cancel}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data={"message": "Order cancelled successfully"}, status=status.HTTP_200_OK
        )


class ServeOrderView(GenericAPIView):
    """
    This endpoint is used to change order status from Pending to Served.
    """

    serializer_class = UpdateOrderSerializer
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request, "action": Actions.Serve}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data={"message": "Order status changed to served successfully"},
            status=status.HTTP_200_OK,
        )
