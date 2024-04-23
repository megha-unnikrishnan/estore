from django.contrib import admin
from shop.models import Category,Author,Book,MultipleImages,Bookreview,Bookvariant,Offer
admin.site.register(Category)
admin.site.register(Author)
admin.site.register(Bookreview)
admin.site.register(Book)
admin.site.register(MultipleImages)
admin.site.register(Bookvariant)
admin.site.register(Offer)


# Register your models here.
