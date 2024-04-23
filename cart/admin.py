from django.contrib import admin
from cart.models import CartItem,Cart,Coupons

admin.site.register(CartItem)
admin.site.register(Cart)
admin.site.register(Coupons)

# Register your models here.
