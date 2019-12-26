"""
generate django.form to build html report filling form.
--> return context dictionary for template renderer
"""

from bootstrap_datepicker_plus import DatePickerInput

from .models import Report
from django import forms
from .forms import ReportFillingForm
from .forms import ServiceMembersChainEditForm
import json


def get_report_filling_form(report_id):
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


# def get_service_members_chain_edit_form(service_members_chain_dict):
#     """return html django form for service members chain editing"""
#     form_content_dict = {}
#
#     for member_id, member in service_members_chain_dict.items():
#         form_content_dict['edit_member_' + str(member_id)] = forms.CharField(
#             # label=member,
#             label=member.rank.name + " " + member.__str__(),
#             widget=forms.HiddenInput()
#         )
#
#     dynamicServiceMembersChainEditForm = type('ServiceMembersChainEditForm', (ServiceMembersChainEditForm,),
#                                               form_content_dict)
#     return dynamicServiceMembersChainEditForm


def parse_report_body_template(text, decoder=json.JSONDecoder()):
    """Parse report body template for substution patterns
       Split all parts into dictionaries for future form creation

    BODY TEMPLATE EXAMPLE:
    there are few json types except regular text inside template to return
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
                initial=field_dict['title']
            )
        elif field_dict['type'] == "int":
            form_content_dict[key] = forms.CharField(
                label="",
                widget=forms.TextInput(attrs={"class": "form-control", 'size': 3}),
                initial=2019
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
                ),
                initial="2019-11-25"
            )
        elif field_dict['type'] == "str":
            form_content_dict[key] = forms.CharField(
                label="",
                help_text=field_dict['title'],
                widget=forms.TextInput(attrs={"class": "form-control", 'size': 100}),
                initial="сімейними обставинами"
            )
        elif field_dict['type'] == "text":
            form_content_dict[key] = forms.CharField(
                label="",
                help_text=field_dict['title'],
                widget=forms.Textarea(attrs={"cols": 120, "rows": 4, "wrap": "hard"}),
                initial="сімейними обставинами"
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
        # elif field_dict['type'] == "new_line":
        #     form_content_dict[key] = forms.CharField(
        #         label="N",
        #         widget=forms.HiddenInput(),
        #         initial=""
        #     )


        # extra field (conter for labels and input fields in form)
        form_content_dict['fields_counter'] = forms.IntegerField(
            label="",
            widget=forms.HiddenInput(),
            initial=len(parts_dict) - 1
        )

    return form_content_dict
