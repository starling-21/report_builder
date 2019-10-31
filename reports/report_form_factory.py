# from .models import Report
# from django import forms
import json




def get_form(report_id):
    report = Report.objects.get(pk=report_id)
    context = {
       'title': report.title,
        'body_sample': report.body_sample,

    }

    # title = models.CharField(max_length=255, null=True)
    # body_sample = models.TextField(blank=True, null=True)
    # body = models.TextField(blank=True, null=True)




def parse_report_body_template(text, decoder=json.JSONDecoder()):
    """Parse report body template for substution patterns
       Split all parts into dictionaries for future form creation

    there are few json types to return
    {
        "type": "label",
        "title": "User text to print",
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
            #append title text
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

    for item in parsed_dict.items():
        print(item)
    return parsed_dict




input_str = """Прошу Вашого клопотання про перенесення мені терміну щорічної основної відпустки за 
        {
            "title": "за який рiк переноситься вiдпустка",
            "type": "int"
        }
        рік з 
        {
            "title": "з якой дати",
            "type": "date",
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
        до пасхи
        """
def main_test():
    parse_report_body_template(text=input_str)

main_test()





#
#
#
# def parse_report_template(request):
# def parse_report_template():
#     """report parse function
#     substitutte pattern:      @_<type>_<label>@
#
#     """
#
#     input_str = """Прошу Вашого клопотання про перенесення мені терміну щорічної основної відпустки за
#     @_int_за какой год переносится отпуск@ рік з @_date_перенести с@ на @_date_перенести на@
#     року у зв’язку з @_str_причина_long@.
#     """
#
#     """_str_причина переноса"""
#     """_date_перенести отпуск с"""
#     """_int_за какой год переносится отпуск"""
#
#     parsed_pattern_dict = {}
#
#     counter = 0
#     for pattertline in input_str.split('@'):
#         temp = {}
#         if pattertline[0] == '_':
#             patter_list = pattertline.split('_')
#
#             temp['insert_type'] = patter_list[1]
#             temp['label'] = patter_list[2]
#             temp['begin'] = input_str.find(pattertline)
#             temp['end'] = temp['begin'] + len(pattertline)
#
#             parsed_pattern_dict[temp['insert_type'] + '_' + str(counter)] = temp
#             counter += 1
#
#     a = 0
#
#     dynamic_fields_dict = {}
#     for key, nested_dict in parsed_pattern_dict.items():
#         if nested_dict['insert_type'].startswith('int'):
#             dynamic_fields_dict[key] = forms.IntegerField(
#                 label=nested_dict['label'],
#             )
#
#         elif nested_dict['insert_type'].startswith('str'):
#             dynamic_fields_dict[key] = forms.CharField(
#                 label=nested_dict['label'],
#                 widget=forms.TextInput(attrs={"class": "form-control"})
#             )
#
#         elif nested_dict['insert_type'].startswith('date'):
#             dynamic_fields_dict[key] = forms.DateField(
#                 label=nested_dict['label'],
#                 widget=DatePickerInput(
#                     format='%Y-%m-%d',
#                     options={
#                         "locale": "ru"
#                     }),
#             )
#     return dynamic_fields_dict