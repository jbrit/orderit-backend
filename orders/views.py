from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response

from orders.serializers import (
    ItemSerializer,
    MakeOrderSerializer,
    MealSerializer,
    OrderSerializer
)
# Create your views here.
class ItemListView(ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = []
    queryset = ItemSerializer.Meta.model.objects.all()


class MealListView(ListAPIView):
    serializer_class = MealSerializer
    permission_classes = []
    queryset = MealSerializer.Meta.model.objects.all()


class OrderListView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = OrderSerializer.Meta.model.objects.all()

    def get(self, request):
        if request.user.is_superuser:
            data = OrderSerializer(self.get_queryset(), many=True).data
            return Response(data)

        data = OrderSerializer(
            OrderSerializer.Meta.model.objects.filter(
                user=request.user
            ),
            many=True,
        ).data
        return Response(data)


class MakeOrderView(GenericAPIView):
    serializer_class = MakeOrderSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid()
        serializer.save()
        message, status, order = serializer.save()
        return Response(data={"message": message, "order":order}, status=status)

#TODO CancelOrderView
#TODO Accept/RejectView
