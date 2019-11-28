from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse

from reports.models import Serviceman
from . import report_content_util
from . import report_forms_util
from .models import Report
from .models import Position
import json

from .forms import ServiceMembersChainEditForm
from . import main_report_controller as report_controller


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
    swap_position_id = None
    if request.method == 'POST':
        serviceman_chain = request.session['serviceman_chain']
        if 'edit_chain_id' in request.POST:
            print("Editing_member with id:", request.POST.get('edit_chain_id'))
            swap_id = int(request.POST.get('edit_chain_id'))
        elif 'edit_position_id' in request.POST:
            print("Editing_member_position with id:", request.POST.get('edit_position_id'))
            swap_position_id = int(request.POST.get('edit_position_id'))
        elif 'submit_new_id' in request.POST:
            old_id = request.POST.get('submit_new_id')
            swap_id = request.POST.get('swap_id')
            print('id swap: {} -> {}'.format(old_id, swap_id))
            for member in serviceman_chain:
                if member.id == int(old_id):
                    replace_index = serviceman_chain.index(member)
            #update position as temp
            positions_list = request.session['positions_list']
            current_position = positions_list[replace_index]
            current_position.temp_supervisor = True
            updated_position = current_position
            #replace member in chain
            new_serviceman = Serviceman.objects.get(id=int(swap_id))
            new_serviceman.position = updated_position
            serviceman_chain[replace_index] = new_serviceman

            request.session['serviceman_chain'] = serviceman_chain
            request.session.modified = True
        elif 'submit_new_position_id' in request.POST:
            old_position_id = request.POST.get('submit_new_position_id')
            swap_position_id = request.POST.get('swap_position_id')
            is_temp = request.POST.getlist('temporary')
            print("position swap: {} --> {}".format(old_position_id, swap_position_id))
            print("TEMP:", request.POST.get('temporary'))
            print("TEMP_list:", request.POST.getlist('temporary'))
            for member in serviceman_chain:
                if member.position.id == int(old_position_id):
                    new_position = Position.objects.get(id=swap_position_id)
                    member.position = new_position
                    print("position changed from {} to {}".format(old_position_id, new_position.id))
            request.session['serviceman_chain'] = serviceman_chain
            request.session.modified = True
        elif 'remove_chain_id' in request.POST:
            remove_id = request.POST.get('remove_chain_id')
            for member in serviceman_chain:
                if member.id == int(remove_id):
                    replace_index = serviceman_chain.remove(member)
            request.session['serviceman_chain'] = serviceman_chain
            request.session.modified = True
        elif 'submit_chain_editing' in request.POST:
            print("submit_chain_editting")

            # print('serviceman chain list:', request.session['serviceman_chain_id_list'])
            return redirect(reverse('reports:reports_list', kwargs={'serviceman_id': serviceman_id}))

    elif request.method == 'GET':
        serviceman = Serviceman.objects.get(id=serviceman_id)
        serviceman_chain = report_content_util.get_servicemen_chain_list(serviceman)

        positions_list = [member.position for member in serviceman_chain]
        request.session['positions_list'] = positions_list
        request.session['serviceman_chain'] = serviceman_chain
        request.session.modified = True

    # positions_list = [member.position.id for member in serviceman_chain]
    # print("positions:", positions_list)
    serviceman_chain = request.session['serviceman_chain']
    context = {
        'serviceman_chain': serviceman_chain,
        'swap_id': swap_id,
        'swap_position_id': swap_position_id
    }
    return render(request, 'reports/edit_service_members_chain.html', context)


def reports_list_view(request, serviceman_id):
    """show reports titles list to choose"""
    # serviceman = Serviceman.objects.get(id=serviceman_id).get_full_name()
    reports_list = Report.objects.all()
    context = {
        'reports_list': reports_list
    }
    return render(request, 'reports/reports_list.html', context)


def report_filling_view(request, report_id):
    """report filling form view"""
    if request.method == 'POST':
        print("Processing filled in report form data:")
        print("Session data:")
        for k, v in request.session.items():
            print("{}:{}".format(k, v))
        # serviceman_chain = request.session['serviceman_chain']
        # report_filepath = report_controller.generate_report(request, serviceman_id, serviceman_chain_id_list)

        report_filepath = report_controller.generate_report(request)
        a = 1
        #TODO return document in new tab after redirect

    # print(request.session['serviceman_chain'])
    context = report_forms_util.get_report_filling_form(report_id)
    return render(request, 'reports/report_filling.html', context)


# ======================================================================================================================
# ======================================================================================================================
# ======================================================================================================================
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


#DOCX GENERATION
# return HttpResponse("REPORT has been generated SUCCESSFULLY")
#     response = FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filepath.split('\\')[-1])
#     # response['Content-Type'] = 'application/octet-stream'
#     # response['Content-Disposition'] = 'attachment;filename="{0}"'.format(filepath.split('\\')[-1]);
#     # response['Content-Length'] = os.path.getsize(filepath)
#     return response;