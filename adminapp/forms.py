from django import forms
from shop.models import Category
class CategoryUpdateform(forms.ModelForm):
    class Meta:
        model=Category
        fields=['category_name','category_desc','category_image','offer']
