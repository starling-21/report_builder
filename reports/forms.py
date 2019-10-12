from django import forms

from .models import Report


class ReportForm_test1(forms.Form):
    date_1 = forms.DateField(label='Введіть дату', input_formats=['%d-%m-%Y'], required=False)
    text_1 = forms.CharField(widget=forms.Textarea(),
                             help_text='Введіть <br> адресу!')











class RepTitleForm(forms.ModelForm):
    class Meta:
        model = Report
        exclude = ['report_fields']


class RepFieldsFrom(forms.Form):
    pass