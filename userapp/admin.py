from django.contrib import admin
from .models import CustomUser,Forgotpassword,UserAddress
from django.contrib.auth.admin import  UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model



admin.site.register(CustomUser)
admin.site.register(Forgotpassword)
admin.site.register(UserAddress)
# Register your models here.
