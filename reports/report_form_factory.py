from bootstrap_datepicker_plus import DatePickerInput

from .models import Report
from django import forms
from .forms import ReportFillingForm
import json


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
            # yield temp_dict
            break
        try:
            # append title text
            parsed_dict[dict_index] = {
                "title": text[prev_pos:match_start],
                "type": "label"
            }
            dict_index += 1

            dict_result, index = decoder.raw_decode(text[match_start:])
            # yield dict_result
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
                widget=forms.HiddenInput()
            )
        elif field_dict['type'] == "int":
            form_content_dict[key] = forms.IntegerField(
                label="",
                # help_text=field_dict['title'],
            )
        elif field_dict['type'] == "date":
            form_content_dict[key] = forms.DateField(
                label="",
                # help_text=field_dict['title'],
                widget=DatePickerInput(
                    format='%Y-%m-%d',
                    options={
                        "locale": "ru"
                    }),
            )
        elif field_dict['type'] == "str":
            form_content_dict[key] = forms.CharField(
                label="",
                help_text=field_dict['title'],
                widget=forms.TextInput(attrs={"class": "form-control"})
            )
        elif field_dict['type'] == "text":
            form_content_dict[key] = forms.CharField(
                label="",
                help_text=field_dict['title'],
                widget=forms.Textarea(attrs={'cols': 100, 'rows': 4, 'width': '30px'})
            )
    return form_content_dict


def get_form_context(request, report_id):
    """parse report template, generate form fields and passes it to template context
    return context for template"""
    report = Report.objects.get(pk=report_id)

    # TODO test string
    report.body = input_str = """Прошу Вашого клопотання про перенесення мені терміну щорічної основної відпустки за
        {
            "title": "за який рiк переноситься вiдпустка",
            "type": "int"
        }
        рік з
        {
            "title": "з якой дати",
            "type": "date"
        }
        на
        {
            "title": "на яку дату",
            "type": "date"
        }
        року у зв’язку з
        {
            "title": "причина переносу_1",
            "type": "str"
        }
        або у зв’язку з
        {
            "title": "причина переносу_2",
            "type": "text"
        }
        .
        """
    report.body_dample = "Прошу Вашого клопотання про перенесення мені терміну щорічної основної відпустки за 2018 "
    "рік з 25 листопада на 21 вересня 2018 року у зв’язку з сімейними обставинами."

    report_template_parsed_dict = parse_report_body_template(report.body)
    report_form_fields = get_raw_form_fields(report_template_parsed_dict)

    dynamicReportFillingForm = type('ReportFillingForm', (ReportFillingForm,), report_form_fields)

    context = {
        'title': report.title,
        'body_sample': report.body_sample,
        'report_fields_form': dynamicReportFillingForm
    }
    return context
