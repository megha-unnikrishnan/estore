from django.urls import path
from .import views

urlpatterns=[
    path('admin-login/',views.admin_login,name='adminlogin'),
    path('admin-dashboard/', views.admin_dashboard, name='admindashboard'),
    path('admin-logout/',views.admin_logout,name='logoutadmin'),

    path('admin-users/',views.admin_users,name='users'),
    path('admin-action/<int:id>/', views.admin_action, name="adminaction"),
    path('admin-add-product/', views.admin_add_product, name="adminaddproduct"),
    path('admin-product/', views.admin_product, name="adminproduct"),
    path('admin-add-author/', views.admin_add_author, name="adminaddauthor"),
    path('admin-edit-author/<int:id>/', views.admin_edit_author, name="admineditauthor"),
    path('admin-author/', views.admin_author, name="adminauthor"),
    path('admin-add-category/', views.admin_add_category, name="adminaddcat"),
    path('admin-category/', views.admin_category, name="admincategory"),
    path('admin-edit-category/<int:id>/', views.admin_edit_category, name="admineditcategory"),
    path('admin-author-action/<int:id>/',views.admin_author_action,name='adminauthoraction'),
    path('admin-product-action/<int:id>/', views.admin_product_action, name='adminproductaction'),
    path('admin-category-action/<int:id>/',views.admin_category_action,name='admincataction'),
    path('admin-edit-product/<int:id>/', views.admin_edit_product, name="admineditproduct"),

    path('admin-edit-offer/<int:id>/', views.admin_edit_offer, name="admineditoffer"),
    path('admin-offer-add/',views.admin_offer_add,name='adminaddoffer'),
    path('admin-offer/',views.admin_offer,name='adminoffer'),
    path('admin-offer-action/<int:id>/', views.admin_offer_action, name='adminofferoraction'),

    path('admin-add-product-variant/',views.add_product_variant,name='productaddvariant'),

    path('admin-edition/',views.admin_edition,name='adminedition'),
    path('admin-add-edition/',views.admin_add_edition,name='adminaddedition'),
    path('admin-edit-edition/<int:id>/',views.admin_edit_edition,name='admineditedition'),
    path('admin-edition-action/<int:id>/', views.admin_edition_action, name='admineditionoraction'),
    path('admin-variant/',views.admin_variant,name='adminvariant'),
    path('admin-variant-edition-action/<int:id>/',views.admin_variant_edition_action,name='adminvariantaction'),
    path('admin-variant-edit/<int:id>/',views.admin_edit_product_variant,name='adminvariantedit'),

    path('delete_image/<int:image_id>/', views.delete_image, name='deleteimage'),


    path('admincoupon/',views.coupon_list,name='coupon'),
    path('admin-add-coupon',views.add_coupon,name='addcoupon'),
    path('admin-coupon-action/<int:id>/',views.admin_coupon_action,name='couponaction'),
    path('admin-edit-coupon/<int:id>/', views.admin_edit_coupon, name='couponedit'),

    path('admin-orders/' ,views.admin_orders,name='adminorder'),
    path('admin-update-orders/<int:id>/',views.admin_order_update,name='adminorderupdate'),

    path('admin-sales-reports/',views.admin_sales_reports,name='adminreports')
]