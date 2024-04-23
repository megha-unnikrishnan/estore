from django.urls import path
from .import views
urlpatterns=[
    path('index/',views.index,name='userindex'),
    path('login/',views.user_login,name='login'),
    path('register/',views.user_signup,name='register'),
    path('logout/',views.user_logout,name='logout'),

    path('otp/<int:id>/',views.otp_verification,name='otp-verification'),
    path('password-reset/',views.user_forgotpassword,name='forgot-password'),
    path('change-password/<token>/',views.change_password,name='change-password'),
    path('product-detail/<int:id>/',views.product_detail,name='productdetail'),
    path('regenerate-otp/<int:id>/', views.regenerate_otp, name="regenerateotp"),
    path('product_list',views.product_list,name='productlist'),
    path('product-list-detail/<int:id>/', views.product_list_detail, name='productlistdetail'),
    path('search/',views.search_view,name='search'),
    # path('suggest/', views.suggest_view, name='suggest'),
    path('category/<int:id>/',views.category_list,name='category'),
    path('category-detail/<int:id>',views.category_detail,name='category-detail'),

    path('userprofile/',views.userprofile,name='userprofile'),
    path('add-address/<int:id>/',views.addaddress,name='addaddress'),
    path('address-book/',views.address_book,name='addressbook'),
    path('delete-book/<int:id>/',views.deleteaddress,name='deleteaddress'),
    path('update-book/<int:id>/<int:o_id>/',views.updateaddress,name='updateaddress'),
    path('change-password',views.changeuserpassword,name='changeuserpassword'),
    path('profiledetails/',views.profiledetails,name='profiledetails'),
    path('updateprofile/',views.updateprofile,name='updateprofile'),
    path('sort/', views.sort_products, name='sort_products'),




]


