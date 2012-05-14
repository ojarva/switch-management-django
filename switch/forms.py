from django import forms
from switch.models import Port

class PortForm(forms.ModelForm):
    class Meta:
        model = Port
        widgets = {
            'switch': forms.HiddenInput(),
            'number': forms.HiddenInput(),
            'expires': forms.DateTimeInput(),
        }

class BulkChangeForm(forms.Form):
    vlan = forms.IntegerField(max_value=255, min_value=0)
    change_default = forms.BooleanField(required=False, 
              help_text="Change port default VLAN too")
    change_locked = forms.BooleanField(required=False, 
              help_text="Change locked ports (discouraged, use with caution)")

class EmptyForm(forms.Form):
    pass
