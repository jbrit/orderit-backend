from django.contrib import admin

from orders.models import Item, Meal, Order, OrderItem

# Register your models here.
class OrderItemTabularInline(admin.TabularInline):
    extra = 1
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "reference",
        "status",
        "vendor",
        "timestamp",
    ]
    # search_fields = [
    #     "transaction__reference",
    #     "user"
    # ]
    inlines = [OrderItemTabularInline]


admin.site.register(Item)
admin.site.register(Meal)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
