from django import forms
from .models import BPMNFile

class BPMNFileForm(forms.ModelForm):
    def clean_xml_data(self):
        xml = self.cleaned_data.get('xml_data')
        if not xml.strip().startswith('<?xml'):
            raise forms.ValidationError("Invalid BPMN XML format")
        return xml