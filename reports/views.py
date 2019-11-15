from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse


from reports.models import Serviceman
from . import report_content_util
from . import report_forms_util
from .models import Report

from .forms import ServiceMembersChainEditForm


# Create your views here.

def report_home_view(request):
    body = "Reports App!"
    body += "<br><br>"
    body += "<a href='/serviceman_list'>Users</a>"
    return HttpResponse(body)


def serviceman_list_view(request):
    """test view for showing users list. For choosing who generate report for"""
    serviceman_list = Serviceman.objects.all()
    context = {
        'serviceman_list': serviceman_list
    }
    return render(request, 'reports/serviceman_list.html', context)


def edit_service_members_chain_view(request, serviceman_id):
    """change servicemen chain if needed"""
    swap_id = None
    if request.method == 'POST':
        if "edit" in request.POST:
            print("edit_member_ ---> id:", request.POST.get('edit'))
        elif "submit_chain_editting" in request.POST:
            print("submit_chain_editting ---> reports list redirect")


        # TODO pass serviceman_id, servicemen_chain further to report list view
        print("POST from ServiceMembersChainEditForm")

        for k, v in request.POST.items():
            if "edit" in v:
                print("Editin user with id:", k)
                swap_id = int(k)
        serviceman = Serviceman.objects.get(id=serviceman_id)
        serviceman_chain = report_content_util.get_servicemen_chain_as_dict(serviceman)

        tier_members_pairs = report_content_util.convert_dict_to_tier_users_pairs(serviceman_chain)
        # request.session['tier_members_pairs'] = tier_members_pairs

        return HttpResponseRedirect(redirect('reports_list', kwargs={'serviceman_id': serviceman_id}))  # does not work
        #TODO redirects
        # return HttpResponseRedirect(reverse('reports:reports_list', kwargs={'serviceman_id':serviceman_id}))  #OK
        # return HttpResponseRedirect(reverse('reports:reports_list', args=(serviceman_id,))) #OK

    serviceman = Serviceman.objects.get(id=serviceman_id)
    serviceman_chain = report_content_util.get_servicemen_chain_as_dict(serviceman)

    context = {
        'serviceman_chain': serviceman_chain,
        'swap_id': swap_id
    }
    return render(request, 'reports/edit_service_members_chain.html', context)


def reports_list_view(request, serviceman_id):
    """show reports titles list to choose"""
    serviceman = Serviceman.objects.get(id=serviceman_id).get_full_name()
    reports_list = Report.objects.all()
    context = {
        'user_id': serviceman_id,
        'user': serviceman,
        'reports_list': reports_list
    }
    return render(request, 'reports/reports_list.html', context)


def report_filling_view(request, serviceman_id, report_id):
    """report filling form view"""
    if request.method == 'POST':
        input_form_data = request.POST.copy()
        # TODO proceed filled in data

    context = report_forms_util.get_report_filling_form(report_id)
    return render(request, 'reports/report_filling.html', context)



# =======================================================================================================================
# =======================================================================================================================
# =======================================================================================================================
# def dyn_form_view(request):
#     """dynamyc form after user submits input"""
#     context = {}
#     form_content = {}
#     new_fields = {}
#
#     if request.method == 'POST':
#         context['show_report_fields_form'] = True
#         report = TestReport()
#
#         # received 'report_title' submit
#         if 'subm_title' in request.POST:
#             # report.report_title = int(request.POST['report_title'])
#             report = TestReport.objects.filter(report_title=int(request.POST['report_title'])).last()
#             if report is None:
#                 report = TestReport()
#                 report.report_title = int(request.POST['report_title'])
#             try:
#                 form_content = json.loads(report.report_fields)
#             except json.JSONDecodeError:
#                 form_content = {}
#         # received 'report fields' submit
#         elif 'subm_fields' in request.POST:
#             report.report_title = int(request.POST['report_title'])
#             for key in request.POST.keys():
#                 if key != 'csrfmiddlewaretoken' and key != 'subm_fields':
#                     form_content[key] = request.POST[key]
#             report.report_fields = json.dumps(form_content)
#             report.save()
#             return redirect('reports:index')
#             # return HttpResponseRedirect(reverse_lazy('reports:index'))
#
#         if report.report_title == -1:
#             new_fields = {}
#         elif report.report_title == 0:
#             new_fields = {
#                 'date_1': forms.DateField(
#                     required=False,
#                     label='Введіть дату!'
#                 ),
#                 'int_1': forms.IntegerField(required=False)
#             }
#         elif report.report_title == 1:
#             new_fields = {
#                 'int_1': forms.IntegerField(required=False),
#                 'date_1': forms.DateField(required=False),
#                 'int_2': forms.IntegerField(required=False)
#             }
#         elif report.report_title == 2:
#             new_fields = {
#                 'start_num_1': forms.IntegerField(required=False),
#                 'end_num_1': forms.IntegerField(required=False)
#             }
#         # new_fields = parse_report_template()
#
#     elif request.method == 'GET':
#         context['show_report_fields_form'] = False
#     ########################################################################################################################
#     dynamicReportFieldsForm = type('RepFieldsFrom', (RepFieldsFrom,), new_fields)
#
#     reportFieldsForm = dynamicReportFieldsForm(form_content)
#     context['report_title_form'] = RepTitleForm(request.POST or None)
#     context['report_fields_form'] = reportFieldsForm
#
#     return render(request, 'reports/rep_dynamic_form.html', context)


# def test_form_view(request):
#     """test view"""
#     if request.method == 'POST':
#         form_2 = ReportForm_test1(request.POST)
#         if form_2.is_valid():
#             print("received:", )
#             for k, v in form_2.cleaned_data.items():
#                 print('{}:{}'.format(k, v))
#             return HttpResponseRedirect(reverse_lazy('reports:index'))
#     else:
#         form_2 = ReportForm_test1()
#     return render(request, 'reports/test_report_1.html', {'form': form_2})


# =======================================================================================================================
# =======================================================================================================================
# =======================================================================================================================
# def generate_report_view(request, user_id=5):
#     """generate test report """
# ----
# TESC BULK report generation
# users = Serviceman.objects.filter(id__gt=1)
# for user in users:
#     sample_user = get_serviceman(user.id)
#     # GET ALL Footers and Headers REPORT CHAIN
#     merge_dict = get_global_report_merge_dict(sample_user)
#
#     if merge_dict is None:
#         return HttpResponse("report generation (___ERROR___)!!!!")
#
#     # TODO add method for report body generation
#     merge_dict.update(get_body_text())
#     generate_report(merge_dict, template_name="template_tier_2.docx", report_name='t2')
#     sleep(1)
# ----


# ---***
# user_id = 5
# user = get_serviceman(user_id)
# # GET ALL Footers and Headers REPORT CHAIN
# merge_dict = get_global_report_merge_dict(user)
#
# if merge_dict is None:
#     return HttpResponse("report generation (___ERROR___)!!!!")
#
# # TODO add method for report body generation
# merge_dict.update(get_report_body_text())
# filepath = generate_report(merge_dict, template_name="template_tier_2.docx", report_name='t2')
#
# # return HttpResponse("REPORT has been generated SUCCESSFULLY")
# return FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filepath.split('\\')[-1])
# ---***


def get_report_body_text():
    """TEST METHOD"""
    body_tier_0 = "Прошу Вашого клопотання про перенесення мені терміну щорічної основної відпустки за 2018 "
    "рік з 25 листопада на 21 вересня 2018 року у зв’язку з сімейними обставинами."

    body_tier_1 = "Клопочу по суті рапорту капітана Василя Шпака"

    body_tier_2 = "Клопочу по суті рапорту капітана Василя Шпака"

    extra_dict = {
        'body_tier_0': body_tier_0,
        'body_tier_1': body_tier_1,
        'body_tier_2': body_tier_2,
    }
    return extra_dict


"""TEST POINT"""

""" REPORT GENERATION SECTION """
from definitions import *
from datetime import datetime
from mailmerge import MailMerge


def generate_report(merge_dict, template_name="template_universal.docx", report_name="rep"):
    """generate report document and return path to it"""
    template_path = os.path.join(TEMPLATES_PATH, template_name)
    document = MailMerge(template_path)
    print("Fields included in {}: {}".format(template_name, document.get_merge_fields()))
    document.merge(**merge_dict)
    now = datetime.now()
    merged_file_path = os.path.join(OUTPUT_PATH, now.strftime("%d %H%M-%S") + '_' + report_name + '.docx')
    document.write(merged_file_path)
    return merged_file_path

# def get_global_report_merge_dict(serviceman):
#     """iterate throught tier's user pairs (if serviceman has a supervisor) and return data for global_merge_dict
#         Format: {tier:{report dict}}
#     """
#     try:
#         global_merge_dict = {}
#         user_pairs_dict = get_tier_users_pairs(serviceman)
#         for tier, users in user_pairs_dict.items():
#             from_user = users[0]
#             to_user = users[1]
#
#             footer_dict = get_footer_data(from_user)
#             footer_dict = append_to_dict_keys(footer_dict, tier)
#             global_merge_dict.update(footer_dict)
#
#             header_dict = get_header_data(to_user)
#             header_dict = append_to_dict_keys(header_dict, tier)
#             global_merge_dict.update(header_dict)
#     except:
#         global_merge_dict = None
#     finally:
#         return global_merge_dict
#
#
# def append_to_dict_keys(dictionary, tier):
#     """adds tier value to every key in a dictionary"""
#     result = {}
#     for key, value in dictionary.items():
#         result[key + str(tier)] = value
#     return result
#
#
# def get_tier_users_pairs(serviceman):
#     """returns dictionary of paired users for report. {tier:(FROM_user, TO_user),....} or NONE"""
#     users_chain = get_servicemen_chain(serviceman)
#     tiers_dict = {}
#     if len(users_chain) < 2:
#         return None
#     elif len(users_chain) == 2:
#         tiers_dict[0] = (users_chain[0], users_chain[1])
#     elif len(users_chain) > 2:
#         for i in range(0, len(users_chain) - 1):
#             tiers_dict[i] = (users_chain[i], users_chain[i + 1])
#     return tiers_dict
#
#
# def get_servicemen_chain(serviceman):
#     """return report's servicemembers chain from initiator too the top level supervisor"""
#     users_list = []
#     users_list.append(serviceman)
#     user = get_supervisor_for(serviceman)
#     if user is not None:
#         users_list.extend(get_servicemen_chain(user))
#     return users_list
#
#
# def get_footer_data(serviceman):
#     """returns footer data dict for certain serviceman"""
#     position = serviceman.position
#     unit = serviceman.unit
#     units_chain = unit.get_all_parents()
#     rank = serviceman.rank.__str__()
#     full_name = serviceman.get_full_name()
#
#     full_position = get_full_position(position.__str__(), units_chain)
#     footer_date_line = get_date_line()
#
#     footer_dict = {
#         'footer_position_tier_': full_position,
#         'footer_rank_tier_': rank,
#         'footer_username_tier_': full_name,
#         'date_line_tier_': footer_date_line
#     }
#
#     # print_footer(footer_dict)
#     return footer_dict
#
#
# def get_header_data(serviceman):
#     """returns header data dict for certain serviceman"""
#     position = serviceman.position.get_to_position()
#     unit = serviceman.unit
#     units_chain = unit.get_all_parents()
#     rank = serviceman.rank.to_name
#     full_name = serviceman.get_full_name_to()
#
#     full_position = get_full_position(position, units_chain)
#
#     header_dict = {
#         'header_position_tier_': full_position,
#         'header_rank_tier_': rank,
#         'header_username_tier_': full_name,
#     }
#
#     # print_header(header_dict)
#     return header_dict
#
#
# def get_full_position(main_position, units_chain):
#     """complete initial main_position with units list user belongs to"""
#     full_position = main_position
#     position_tail = ""
#
#     if (len(units_chain) > 0): position_tail = units_chain[len(units_chain) - 1].name
#     for i in range(0, len(units_chain) - 1):
#         full_position = full_position + " " + units_chain[i].name
#
#     if (position_tail is not ""):
#         full_position = full_position + "\n" + position_tail
#     return full_position
#
#
# def get_supervisor_for(serviceman):
#     """return supervisor for certain user"""
#     serviceman = serviceman
#     is_supervisor = serviceman.position.supervisor or serviceman.position.temp_supervisor
#     if is_supervisor:
#         unit_supervisor_position = Position.objects.filter(Q(unit=serviceman.unit.parent_unit),
#                                                            Q(temp_supervisor=True) | Q(supervisor=True)).first()
#     else:
#         unit_supervisor_position = Position.objects.filter(Q(unit=serviceman.unit),
#                                                            Q(temp_supervisor=True) | Q(supervisor=True)).first()
#     supervisor = Serviceman.objects.filter(position=unit_supervisor_position).first()
#     return supervisor
#
#
# def get_serviceman(user_id):
#     """returns serviceman vith select related fields: rank, unit and position"""
#     return Serviceman.objects.filter(pk=user_id).select_related('rank', 'unit', 'position').first()
#
#
# def get_report_tiers_count(serviceman):
#     """return report TIER level for serviceman"""
#     tiers_chain = serviceman.unit.get_all_parents(include_self=True)
#     tiers_counter = len(tiers_chain)
#     is_supervisor = serviceman.position.supervisor or serviceman.position.temp_supervisor
#     if is_supervisor:
#         tiers_counter -= 1
#     print("units chain for: {}, counter: {}, list: {}".format(serviceman, tiers_counter, tiers_chain))
#     return tiers_counter
#
#
# def get_date_line():
#     """return properly formated date line for report"""
#     from datetime import datetime
#     monthes = {
#         1: "січня",
#         2: "лютого",
#         3: "березня",
#         4: "квітня",
#         5: "травня",
#         6: "червня",
#         7: "липня",
#         8: "серпня",
#         9: "вересня",
#         10: "жовтня",
#         11: "листопада",
#         12: "грудня",
#     }
#
#     month_numb = datetime.now().month
#     year = datetime.now().year
#     return '"___"' + ' ' + monthes[month_numb] + ' ' + str(year) + ' ' + 'року'
#
#
# def print_footer(footer_dict):
#     print("\n\nFROM:______ %s______" % footer_dict['footer_username_tier_'])
#     for k, v in footer_dict.items():
#         print("{} : {}".format(k, v))
#
#
# def print_header(headeer_dict):
#     print("\n\nTO  :______ %s______" % headeer_dict['header_username_tier_'])
#     for k, v in headeer_dict.items():
#         print("{} : {}".format(k, v))
