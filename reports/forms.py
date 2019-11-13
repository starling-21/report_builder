from django import forms

from bootstrap_datepicker_plus import DatePickerInput

from .models import TestReport

class ServiceMembersChainEditForm(forms.Form):
    pass

class ReportFillingForm(forms.Form):
    pass

# class ReportForm_test1(forms.Form):
#
#     date_1 = forms.DateField(
#         label='Введіть дату',
#         widget=DatePickerInput(
#             format='%Y-%m-%d',
#             options={
#                 "locale": "ru"
#             }),
#         error_messages={'invalid': 'дата не правильна'}
#     )
#
#     date_2 = forms.DateField(
#         label='Введіть дату',
#         widget=DatePickerInput(format='%m/%d/%Y'),
#         error_messages={'invalid': 'дата не правильна'}
#     )
#
#     text_1 = forms.CharField(
#         label='Введіть адресу!',
#         widget=forms.TextInput(attrs={"class": "form-control"})
#     )
#
#
#
# #TEST CASE section
# class RepTitleForm(forms.ModelForm):
#     class Meta:
#         model = TestReport
#         exclude = ['report_fields']
#
#
# class RepFieldsFrom(forms.Form):
#     pass
