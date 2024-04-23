from django.contrib import admin
from order.models import Payments,Order,OrderProduct
admin.site.register(Payments)
admin.site.register(Order)
admin.site.register(OrderProduct)
# Register your models here.
