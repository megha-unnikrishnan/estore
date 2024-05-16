from django.urls import path
from .import views
urlpatterns=[
    path('cart/<int:id>/',views.cart_items,name='cart'),
    path('add-to-cart/<int:id>/',views.add_to_cart,name='add_to_cart'),
    path('cart-delete/<int:id>',views.delete_cart_item,name='deletecart'),
    path('cart/update_cart_quantity', views.update_cart_quantity,name='update_cart_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout-view/<int:id>/',views.checkout_view,name='checkoutview'),
    path('suggest_page_view/',views.suggest_page_view,name='suggest_page_view'),
    path('remove_coupon/', views.remove_coupon, name='remove_coupon'),
    path('confirm_order/', views.confirm_order, name='confirm_order'),



]