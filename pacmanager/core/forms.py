from django import forms
from .models import Key, Corporation

class KeyForm(forms.ModelForm):

    class Meta:
        model = Key
        fields = ('keyid', 'vcode')


class CorporationContactForm(forms.ModelForm):

	class Meta:
		model = Corporation
		fields = ('contact',)

		
class ManualAdjustmentForm(forms.Form):
	
	corporation = forms.ModelChoiceField(queryset=Corporation.objects.all(), empty_label=None)
	amount = forms.DecimalField(max_digits=20, decimal_places=2)
	comment = forms.CharField(max_length=255)