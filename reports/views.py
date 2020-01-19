import os
import datetime
from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse

from reports.models import Serviceman
from .models import Report
import json

from . import main_report_controller as report_controller
from . import report_content_util
from . import report_forms_util


# Create your views here.
def index_view(request):
    """show few report generation option for user (basic report or custom_template)"""
    return render(request, 'reports/index.html')


def reports_list_view(request):
    """show all reports"""
    reports_list = Report.objects.all()
    context = {
        'reports_list': reports_list,
    }
    return render(request, 'reports/reports_list.html', context)


def proceed_chosen_report_view(request, report_id):
    """
    proceed choosed report and define next step (show report filling form or users list to set up report owner )
    """
    request.session['report_id'] = report_id
    request.session.modified = True

    report = Report.objects.get(id=report_id)
    if report.type == 'regular':
        return redirect(reverse('reports:users'))
    elif report.type == 'custom':
        return redirect(reverse('reports:edit_service_members_chain'))


def serviceman_list_view(request):
    """test view for showing users list. For choosing who generate report for"""
    serviceman_list = Serviceman.objects.all()
    context = {
        'serviceman_list': serviceman_list
    }
    return render(request, 'reports/serviceman_list.html', context)


def edit_service_members_chain_view(request, serviceman_id=None):
    """change servicemen chain if needed.
    automatically change member position and make him temporary boss on this position"""

    if request.method == 'POST':
        try:
            serviceman_chain = request.session['serviceman_chain']
            if 'edit_chain_id' in request.POST:
                print("Editing_member with id:", request.POST.get('edit_chain_id'))
                swap_id = int(request.POST.get('edit_chain_id'))

            elif 'submit_new_id' in request.POST:
                old_id = request.POST.get('submit_new_id')
                swap_id = request.POST.get('swap_id')
                if (swap_id is not None) and (old_id != swap_id): #and (len(swap_id) > 0)
                    # print('id swap: {} -> {}'.format(old_id, swap_id))
                    for member in serviceman_chain:
                        if member.id == int(old_id):
                            replace_index = serviceman_chain.index(member)

                    new_serviceman = Serviceman.objects.get(id=int(swap_id))

                    initial_member_position = request.session['initial_serviceman_chain'][replace_index].position
                    # change position to temporary and unit
                    if new_serviceman.position != initial_member_position:
                        initial_member_position.temp_supervisor = True
                        initial_member_unit = request.session['initial_serviceman_chain'][replace_index].unit

                        # replace member in chain
                        new_serviceman.position = initial_member_position
                        new_serviceman.unit = initial_member_unit
                    serviceman_chain[replace_index] = new_serviceman

                    request.session['serviceman_chain'] = serviceman_chain
                    request.session.modified = True

                    # change swap_id for proper template rendering (show 'next' button after editing)
                    swap_id = None
            elif 'remove_chain_id' in request.POST:
                remove_id = request.POST.get('remove_chain_id')
                for member in serviceman_chain:
                    if member.id == int(remove_id):
                        serviceman_chain.remove(member)
                request.session['serviceman_chain'] = serviceman_chain
                request.session.modified = True
                swap_id = None
            elif 'submit_chain_editing' in request.POST:
                # print("submit_chain_editting")
                return redirect(reverse('reports:report_filling'))
        except Exception as e:
            print(e)
            return redirect(reverse('reports:edit_service_members_chain', kwargs={'report_id': request.session['report_id']}))
            # return redirect(reverse('reports:users'))

    elif request.method == 'GET':
        swap_id = None
        report_id = request.session['report_id']

        if serviceman_id is None:
            serviceman_chain = report_content_util.get_servicemen_chain_list(report_id)
        else:
            request.session['serviceman_id'] = serviceman_id
            request.session.modified = True
            serviceman = Serviceman.objects.get(id=serviceman_id)
            serviceman_chain = report_content_util.get_servicemen_chain_list(report_id, serviceman)

        request.session['serviceman_chain'] = serviceman_chain
        request.session['initial_serviceman_chain'] = serviceman_chain
        request.session.modified = True

    serviceman_chain = request.session['serviceman_chain']
    context = {
        'serviceman_chain': serviceman_chain,
        'swap_id': swap_id,
    }
    return render(request, 'reports/edit_service_members_chain.html', context)


def report_filling_view(request):
    """report filling form view"""
    if request.method == 'POST':
        document_file_path = report_controller.generate_report(request)
        request.session['report_file_path'] = document_file_path
        request.session.modified = True
        return redirect(reverse('reports:final_report'))

    report_id = request.session['report_id']
    context = report_forms_util.get_report_body_filling_form(report_id)
    return render(request, 'reports/report_filling.html', context)


def return_report_document_view(request):
    """
    generate final document report
    :return: report docx report
    """

    document_file_path = request.session['report_file_path']
    response = FileResponse(open(document_file_path, 'rb'), as_attachment=True,
                            filename=document_file_path.split('\\')[-1])

    now = datetime.datetime.now()
    download_report_file_name = 'report ' + now.strftime("%Y-%m-%d_%H-%M") + '.' + document_file_path.rsplit('.', 1)[-1]
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(download_report_file_name);
    response['Content-Length'] = os.path.getsize(document_file_path)
    return response


def member_search_view(request):
    """
    Search for servicemember and return objects json array:
    :param request:
    :return: default format is - [{id:'member_id', text:'name_representation'}]
    if name_format is defined in search params - format becomes as - [{id:'name_representation', text:'name_representation'}]
    """
    # print("Search request, method", request.method)
    service_members_list = []
    if request.method == 'POST':
        filter_param = request.POST.get('filter_param')
        name_format = request.POST.get('name_format')

        if filter_param is not None and len(filter_param) > 0:
            query_set = Serviceman.objects.filter(
                Q(first_name__icontains=filter_param)
                |
                Q(last_name__icontains=filter_param)
                |
                Q(rank__name__icontains=filter_param)
            )
        else:
            query_set = Serviceman.objects.all()

        if name_format == 'rank-fname-lname':
            for member in query_set:
                member_representation = member.rank.__str__() + ' ' + member.get_first_last_name()
                service_members_list.append({'id': member_representation, 'text': member_representation})
        elif name_format == 'rank-lname-fname':
            for member in query_set:
                member_representation = member.rank.__str__() + ' ' + member.get_last_first_name()
                service_members_list.append({'id': member_representation, 'text': member_representation})
        elif name_format == 'fname-lname':
            for member in query_set:
                member_representation = member.get_first_last_name()
                service_members_list.append({'id': member_representation, 'text': member_representation})
        elif name_format == 'lname-fname':
            for member in query_set:
                member_representation = member.get_last_first_name()
                service_members_list.append({'id': member_representation, 'text': member_representation})
        else:
            # default representation: {id:rank_first_name_last_name}
            for member in query_set:
                member_representation = member.rank.__str__() + ' ' + member.get_first_last_name()
                service_members_list.append({'id': member.id, 'text': member_representation})
        return HttpResponse(json.dumps(service_members_list))

    context = {
        'service_members_list': service_members_list,
    }
    return render(request, 'reports/test_search_user.html', context)
