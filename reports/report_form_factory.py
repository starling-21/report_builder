"""generate django forms for reports"""

from bootstrap_datepicker_plus import DatePickerInput

from .models import Report
from django import forms
from .forms import ReportFillingForm
import json

def get_report_filling_form(request, report_id):
    """parse report template, generate form fields. Return context for html template"""
    report = Report.objects.get(pk=report_id)
    report_template_parsed_dict = parse_report_body_template(report.body)
    report_form_fields = get_raw_form_fields(report_template_parsed_dict)

    dynamicReportFillingForm = type('ReportFillingForm', (ReportFillingForm,), report_form_fields)

    context = {
        'title': report.title,
        'body_sample': report.body_sample,
        'report_fields_form': dynamicReportFillingForm
    }
    return context


def parse_report_body_template(text, decoder=json.JSONDecoder()):
    """Parse report body template for substution patterns
       Split all parts into dictionaries for future form creation

    there are few json types to return
    {
        "type": "label",
        "title": "User text to print",
    }
    {
        "type": "int",
        "title": "за який рiк переноситься вiдпустка"
    }
    {
        "type": "date",
        "title": "з якой дати"
    }
    {
        "type": "str",
        "title": "причина переносу_1"
    }
    {
        "type": "text",
        "title": "причина переносу_2"
    }
    """
    parsed_dict = {}

    pos = 0
    prev_pos = 0
    dict_index = 0
    while True:
        match_start = text.find('{', pos)
        if match_start == -1:
            parsed_dict[dict_index] = {
                "title": text[prev_pos:],
                "type": "label"
            }
            dict_index += 1
            break
        try:
            # append title text
            parsed_dict[dict_index] = {
                "title": text[prev_pos:match_start],
                "type": "label"
            }
            dict_index += 1

            dict_result, index = decoder.raw_decode(text[match_start:])
            parsed_dict[dict_index] = dict_result
            dict_index += 1

            pos = match_start + index
            prev_pos = pos
        except ValueError:
            pos = match_start + 1

    return parsed_dict


def get_raw_form_fields(parts_dict):
    """iterate throught dict and prepare django form for user"""
    form_content_dict = {}
    for key, field_dict in parts_dict.items():

        if field_dict['type'] == "label":
            form_content_dict[key] = forms.CharField(
                label=field_dict['title'],
                widget=forms.HiddenInput(),
            )
        elif field_dict['type'] == "int":
            form_content_dict[key] = forms.CharField(
                label="",
                # error_messages={"mst1": field_dict['title']},
                widget=forms.TextInput(attrs={"class": "form-control", 'size': 3})
            )
        elif field_dict['type'] == "date":
            form_content_dict[key] = forms.DateField(
                label="",
                widget=DatePickerInput(
                    attrs={'size': 7},
                    format='%Y-%m-%d',
                    options={
                        "locale": "ru",
                    },
                )
            )
        elif field_dict['type'] == "str":
            form_content_dict[key] = forms.CharField(
                label="",
                help_text=field_dict['title'],
                widget=forms.TextInput(attrs={"class": "form-control", 'size': 100})
            )
        elif field_dict['type'] == "text":
            form_content_dict[key] = forms.CharField(
                label="",
                help_text=field_dict['title'],
                widget=forms.Textarea(attrs={"cols": 120, "rows": 4, "wrap": "hard"})
            )
    return form_content_dict


