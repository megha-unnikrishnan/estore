from django.urls import path
from . import views

urlpatterns = [

    path('wishlist_view', views.wishlistview, name='wishlist_view'),
    path('add_to_wishlist/<int:id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_wishlist/<int:id>/', views.wishlist_remove, name='remove_wishlist'),
    path('wish-list', views.add_to_wishlist, name='wishlist')

]
