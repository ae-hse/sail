from django import forms
from exploration.models import Entity

class NewEntityForm(forms.ModelForm):
    class Meta:
        model = Entity
        exclude = ('deleted', 'content_type', 'object_id', 'created')