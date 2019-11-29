from django.http import HttpResponse, HttpResponseRedirect
from django.http import FileResponse
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
        # elif 'edit_position_id' in request.POST:
        #     print("Editing_member_position with id:", request.POST.get('edit_position_id'))
        #     swap_position_id = int(request.POST.get('edit_position_id'))
        elif 'submit_new_id' in request.POST:
            old_id = request.POST.get('submit_new_id')
            swap_id = request.POST.get('swap_id')
            print('id swap: {} -> {}'.format(old_id, swap_id))
            for member in serviceman_chain:
                if member.id == int(old_id):
                    replace_index = serviceman_chain.index(member)






            #change position to temporary and unit
            initial_member_position = request.session['initial_serviceman_chain'][replace_index].position
            initial_member_position.temp_supervisor = True
            initial_member_unit = request.session['initial_serviceman_chain'][replace_index].unit
            #replace member in chain
            new_serviceman = Serviceman.objects.get(id=int(swap_id))
            new_serviceman.position = initial_member_position
            new_serviceman.unit = initial_member_unit
            serviceman_chain[replace_index] = new_serviceman

            request.session['serviceman_chain'] = serviceman_chain
            request.session.modified = True
        elif 'remove_chain_id' in request.POST:
            remove_id = request.POST.get('remove_chain_id')
            for member in serviceman_chain:
                if member.id == int(remove_id):
                    serviceman_chain.remove(member)
            request.session['serviceman_chain'] = serviceman_chain
            request.session.modified = True
        elif 'submit_chain_editing' in request.POST:
            print("submit_chain_editting")

            # print('serviceman chain list:', request.session['serviceman_chain_id_list'])
            a = reverse('reports:reports_list', kwargs={'serviceman_id': serviceman_id})
            return redirect(reverse('reports:reports_list', kwargs={'serviceman_id': serviceman_id}))

    elif request.method == 'GET':
        serviceman = Serviceman.objects.get(id=serviceman_id)
        serviceman_chain = report_content_util.get_servicemen_chain_list(serviceman)
        request.session['serviceman_chain'] = serviceman_chain
        request.session['initial_serviceman_chain'] = serviceman_chain
        request.session.modified = True

    serviceman_chain = request.session['serviceman_chain']
    context = {
        'serviceman_chain': serviceman_chain,
        'swap_id': swap_id,
        # 'swap_position_id': swap_position_id
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

        document_file_path = report_controller.generate_report(request)
        #TODO pass params NOT in URL
        request.session['report_file_path'] = document_file_path
        request.session.modified = True
        # return redirect(reverse(test_view_1))
        return redirect(reverse('reports:final_report'))

    context = report_forms_util.get_report_filling_form(report_id)
    return render(request, 'reports/report_filling.html', context)


def test_view_1(request):
    return HttpResponse("<h1>Redirect is DONE!</h1>")


def return_report_document_view(request):
    """
    generate final document report
    :return: report docx report
    """
    # response = FileResponse(open(document_file_path, 'rb'), as_attachment=True, filename=document_file_path.split('\\')[-1])

    # response['Content-Type'] = 'application/octet-stream'
    # response['Content-Disposition'] = 'attachment;filename="{0}"'.format(filepath.split('\\')[-1]);
    # response['Content-Length'] = os.path.getsize(filepath)
    # return response;
    return HttpResponse("<return_report_document_view> : {}".format(request.session['report_file_path']))


#DOCX GENERATION
# return HttpResponse("REPORT has been generated SUCCESSFULLY")
#     response = FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filepath.split('\\')[-1])
#     # response['Content-Type'] = 'application/octet-stream'
#     # response['Content-Disposition'] = 'attachment;filename="{0}"'.format(filepath.split('\\')[-1]);
#     # response['Content-Length'] = os.path.getsize(filepath)
#     return response;