from django.urls import path

from orders.views import (
    CancelOrderView,
    ItemCreateView,
    ItemListView,
    ItemRetrieveUpdateView,
    MakeOrderView,
    MealCreateView,
    MealListView,
    MealRetrieveUpdateView,
    OrderListView,
    OrderRetrieveView,
    ServeOrderView,
)

app_name = "orders"

urlpatterns = [
    path("items/", ItemListView.as_view(), name="items"),
    path("items/create/", ItemCreateView.as_view(), name="item_create"),
    path("items/<int:pk>/", ItemRetrieveUpdateView.as_view(), name="item"),
    path("meals/", MealListView.as_view(), name="meals"),
    path("meals/create", MealCreateView.as_view(), name="meal_create"),
    path("meals/<int:pk>/", MealRetrieveUpdateView.as_view(), name="meal"),
    path("orders/", OrderListView.as_view(), name="orders"),
    path("orders/<int:pk>/", OrderRetrieveView.as_view(), name="order"),
    path("make-order/", MakeOrderView.as_view(), name="make_order"),
    path("cancel-order/", CancelOrderView.as_view(), name="cancel_order"),
    path("serve-order/", ServeOrderView.as_view(), name="serve_order"),
]
