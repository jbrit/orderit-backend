from django.urls import path

from orders.views import (
    CancelOrderView,
    ItemListView,
    MakeOrderView,
    MealListView,
    OrderListView,
    OrderRetrieveView,
    ServeOrderView,
)

app_name = "orders"

urlpatterns = [
    path("items/", ItemListView.as_view(), name="items"),
    path("meals/", MealListView.as_view(), name="meals"),
    path("orders/", OrderListView.as_view(), name="orders"),
    path("order/<int:pk>/", OrderRetrieveView.as_view(), name="order"),
    path("make-order/", MakeOrderView.as_view(), name="make_order"),
    path("cancel-order/", CancelOrderView.as_view(), name="cancel_order"),
    path("serve-order/", ServeOrderView.as_view(), name="serve_order"),
]
