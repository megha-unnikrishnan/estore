from datetime import date
from userapp.models import CustomUser
from django.db import models
from django.shortcuts import reverse
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from decimal import Decimal



def validate_expiry_date(value):
    min_date = date.today()
    if value < min_date:
        raise ValidationError(
            (f"Expiry date cannot be earlier than {min_date}.")
        )


class Offer(models.Model):
    name = models.CharField(max_length=100)
    off_percent = models.PositiveBigIntegerField()
    start_date = models.DateField(validators=[validate_expiry_date])
    end_date = models.DateField()
    is_active = models.BooleanField(default=True, blank=True)

    class Meta:
        ordering=['id']

    def __str__(self):
        return self.name

    def is_expired(self):
        print("date :::::::::::", date.today())
        if self.end_date < date.today():
            return True
        return False
class Category(models.Model):
    category_name = models.CharField(max_length=150,unique=True)
    slug = models.SlugField(max_length=150, unique=True,blank=True)
    category_desc = models.TextField()
    category_image = models.ImageField(upload_to='category_image')
    offer = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    offer_cat=models.ForeignKey(Offer,models.CASCADE,null=True)
    max_discount=models.PositiveBigIntegerField(null=True)

    def __str__(self):
        return self.category_name


    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering=['id']

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    def save(self, *args, **kwargs):
        value = self.category_name
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)

class Author(models.Model):
    author_name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=100, unique=True)
    author_image = models.ImageField(upload_to='author_image')
    author_desc = models.TextField()
    dummy=models.CharField(max_length=50,null=True)
    is_active = models.BooleanField(default=True)


    class Meta:
        verbose_name = 'Author'
        ordering=['id']


    def __str__(self):
        return self.author_name


    def save(self, *args, **kwargs):
        value = self.author_name
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)


class Book(models.Model):
    product_name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    product_image = models.ImageField(upload_to='product_images', blank=True)
    product_desc = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    review=models.TextField(null=True)

    class Meta:
        ordering = ['product_name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def get_url(self):
        return reverse('adminproduct', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

    def save(self, *args, **kwargs):
        value = self.product_name
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)




class Editions(models.Model):
    edition_name=models.CharField(max_length=150)
    slug=models.SlugField(max_length=100,unique=True,blank=True)
    edition_desc=models.TextField()
    year=models.PositiveIntegerField(null=True)
    publisher=models.CharField(max_length=100,null=True)
    is_active=models.BooleanField(default=True, blank=True)

    def __str__(self):
        return self.edition_name

    class Meta:
        ordering=['id']



    def save(self, *args, **kwargs):
        value = self.edition_name
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)

class Bookvariant(models.Model):
    variant_name = models.CharField(max_length=350, blank=True)
    slug=models.SlugField(max_length=200)
    product = models.ForeignKey(Book, on_delete=models.CASCADE,null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE,null=True)
    edition=models.ForeignKey(Editions,on_delete=models.CASCADE,null=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2,blank=True)
    stock = models.PositiveIntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True)
    rating = models.IntegerField()
    max_quantity_per_person = models.PositiveIntegerField(default=4)

    class Meta:
        ordering=['id']

    def save(self, *args, **kwargs):
        value = self.variant_name
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.variant_name

    def discounted_price(self):
        if self.offer:
            discount_percent = Decimal(self.offer.off_percent)
            discount_amount = (discount_percent / Decimal(100)) * self.product_price
            discounted_price = self.product_price - discount_amount
            return discounted_price
        else:
            return self.product_price


class MultipleImages(models.Model):
    product = models.ForeignKey(Bookvariant, on_delete=models.CASCADE)
    images = models.ImageField(upload_to='multiple_images', blank=True)

    def __str__(self):
        return self.product.product.product_name



class Bookreview(models.Model):
    book = models.ForeignKey(Bookvariant, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    rating = models.IntegerField(default=0)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Bookvariant, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.product.variant_name








