from django import forms
from models import FObject

class ObjectForm(forms.ModelForm):
    class Meta:
        model = FObject
        fields = ('name', 'description')