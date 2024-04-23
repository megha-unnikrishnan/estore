from django import forms
from userapp.models import CustomUser
class Updateform(forms.ModelForm):
    class Meta:
        model=CustomUser
        fields=['first_name','last_name','email','phone']