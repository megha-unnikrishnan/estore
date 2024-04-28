from django.db import models
from django.utils import timezone

from userapp.models import CustomUser
from shop.models import Bookvariant
from userapp.models import UserAddress
from django.core.exceptions import ValidationError
from datetime import date

def validate_expiry_date(value):
    min_date = date.today()
    if value < min_date:
        raise ValidationError(
            (f"Expiry date cannot be earlier than {min_date}.")
        )

class Coupons(models.Model):
    coupon_code = models.CharField(max_length=15)
    min_amount = models.PositiveBigIntegerField()
    off_percent = models.PositiveBigIntegerField()
    max_discount = models.PositiveBigIntegerField()
    coupon_stock = models.PositiveIntegerField(null=True, blank=True)
    expiry_date = models.DateField(validators=[validate_expiry_date],null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.coupon_code

    class Meta:
        ordering=['id']

    def is_expired(self):
        """
        Check if the coupon has expired.
        """
        return self.expiry_date < timezone.now().date()


class Cart(models.Model):
    cart_id = models.CharField(unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    coupon = models.ForeignKey(Coupons, on_delete=models.SET_NULL, null=True, blank=True)
    tax = models.FloatField(null=True)

    def __str__(self):
        return str(self.cart_id)







class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Bookvariant, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    is_acitve = models.BooleanField(default=True)
    created_date=models.DateTimeField(auto_now_add=True,null=True)


    def sub_total(self):
        return self.product.discounted_price() * self.quantity

    def __str__(self):
        return self.product.product.product_name

    def sub_total_with_category_offer(self):
        result = int((self.sub_total()) - (self.sub_total() * self.product.category.offer_cat.off_percent) / 100)
        if self.product.category.max_discount is not None:
            if result > self.product.category.max_discount:
                result = self.product.category.max_discount
        return result












# Create your models here.
