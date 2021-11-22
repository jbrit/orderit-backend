from django.urls import path

from orders.views import ItemListView, MakeOrderView, MealListView, OrderListView

app_name = "orders"

urlpatterns = [
    path("items/", ItemListView.as_view(), name="items"),
    path("meals/", MealListView.as_view(), name="meals"),
    path("orders/", OrderListView.as_view(), name="orders"),
    path("make-order/", MakeOrderView.as_view(), name="make_order"),
]
