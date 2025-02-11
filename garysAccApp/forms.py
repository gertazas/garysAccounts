from django import forms
from .models import TrailerSelection

class TrailerSelectionForm(forms.ModelForm):
    class Meta:
        model = TrailerSelection
        fields = ['coffee_percentage', 'milkshake_percentage']
