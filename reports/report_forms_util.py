"""
generate django.form to build html report filling form.
--> return context dictionary for template renderer
"""

from bootstrap_datepicker_plus import DatePickerInput

from .models import Report
from django import forms
from .forms import ReportFillingForm
import json


def get_report_body_filling_form(report_id):
    """parse report body template, generate template context with form fields.
    Return context for html template"""
    report = Report.objects.get(pk=report_id)
    parsed_report_body_template_dict = parse_report_body_template(report.body_template)
    report_body_form_fields = get_raw_django_form_fields(parsed_report_body_template_dict)

    dynamicReportFillingForm = type('ReportFillingForm', (ReportFillingForm,), report_body_form_fields)

    context = {
        'title': report.title,
        'body_sample': report.body_sample,
        'report_fields_form': dynamicReportFillingForm
    }
    return context


def parse_report_body_template(text, decoder=json.JSONDecoder()):
    """Parse report body template by substitution patterns (regular json format with predefined keys)
       Split all parts into dictionaries for future processing

       :return parsed template dictionary

    BODY TEMPLATE EXAMPLE:
    --------------------------------------------------------------------------------------------------------------------
    Прошу Вашого клопотання про перенесення мені терміну щорічної основної відпустки за {"type": "int"} рік
    з {"type": "date"} на {"type": "date"} року у зв’язку з {"type": "str"} або
    у зв’язку з {"type": "text"}.
    Шановний, для перенесення терміну щорічної основної відпустки ви
    маєте зробити речі, які до цього часу не міг зробити ніхто....
    {"type":"first_name_last_name"}
    {"type":"last_name_first_name"}
    {"type":"rank_first_name_last_name"}
    {"type":"rank_last_name_first_name"}
    --------------------------------------------------------------------------------------------------------------------
    every part of template will be parsed (even if it's a regular text) and putted to to dictionary

    IMPORTANT: (regular text automatically parsed to json like this)
    {
        "type": "label",
        "title": "User text to print",
    }

    possible template tags parser can recognize:

    {"type": "int"}
    {"type": "date"}
    {"type": "str"}
    {"type": "text"}

    {"type":"rank_first_name_last_name"}
    {"type":"rank_last_name_first_name"}
    {"type":"first_name_last_name"}
    {"type":"last_name_first_name"}
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


def get_raw_django_form_fields(parts_dict):
    """iterate throughout dict and prepare django form dictionary for django template"""
    form_content_dict = {}

    for key, field_dict in parts_dict.items():

        if field_dict['type'] == "label":
            form_content_dict[key] = forms.CharField(
                label=field_dict['title'],
                widget=forms.HiddenInput(),
                initial=field_dict['title']
            )
        elif field_dict['type'] == "int":
            form_content_dict[key] = forms.CharField(
                label="",
                widget=forms.TextInput(attrs={"class": "form-control", 'size': 3}),
            )
        elif field_dict['type'] == "date":
            form_content_dict[key] = forms.DateField(
                label="",
                widget=DatePickerInput(
                    attrs={"class": "form-control", 'size': 7},
                    format='%Y-%m-%d',
                    options={
                        "locale": "ru",
                    },
                ),
            )
        elif field_dict['type'] == "str":
            form_content_dict[key] = forms.CharField(
                label="",
                help_text=field_dict['title'],
                widget=forms.TextInput(attrs={"class": "form-control", 'size': 80}),
            )
        elif field_dict['type'] == "text":
            form_content_dict[key] = forms.CharField(
                label="",
                help_text=field_dict['title'],
                widget=forms.Textarea(attrs={"class": "form-control", "cols": 100, "rows": 4, "wrap": "hard"}),
            )
        elif field_dict['type'] == "rank_first_name_last_name":
            form_content_dict[key] = forms.CharField(
                label="",
                widget=forms.Select(attrs={"title": "rank-fname-lname"}),
            )
        elif field_dict['type'] == "rank_last_name_first_name":
            form_content_dict[key] = forms.CharField(
                label="",
                widget=forms.Select(attrs={"title": "rank-lname-fname"}),
            )
        elif field_dict['type'] == "first_name_last_name":
            form_content_dict[key] = forms.CharField(
                label="",
                widget=forms.Select(attrs={"title": "fname-lname"}),
            )
        elif field_dict['type'] == "last_name_first_name":
            form_content_dict[key] = forms.CharField(
                label="",
                widget=forms.Select(attrs={"title": "lname-fname"}),
            )




        # extra field (conter for labels and input fields in form)
        form_content_dict['fields_counter'] = forms.IntegerField(
            label="",
            widget=forms.HiddenInput(),
            initial=len(parts_dict) - 1
        )

    return form_content_dict
