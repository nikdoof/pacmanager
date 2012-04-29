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
	
	corporation = forms.ModelChoiceField(queryset=Corporation.objects.all(), empty_label=None, help_text="Corporation you wish to apply the adjustment to")
	amount = forms.DecimalField(max_digits=20, decimal_places=2, help_text="The amount in ISK you wish to adjust the corporation's account by")
	comment = forms.CharField(max_length=255, help_text="Free-form comment to describe this transaction")
