from django import forms
from models import FObject, FAttribute

class ObjectForm(forms.ModelForm):

    class Meta:
        model = FObject
        fields = ('name', 'description')

class AttributeForm(forms.ModelForm):

	class Meta:
		model = FAttribute
		fields = ('name', 'description')