"""military_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from . import views

app_name = "reports"

urlpatterns = [

    # path('', views.index_view, name='index'),

    path('', views.reports_list_view, name='index'),

    path('reports_list', views.reports_list_view, name='reports_list'),
    path('proceed_chosen_report/<int:report_id>', views.proceed_chosen_report_view, name='proceed_chosen_report'),

    path('serviceman_list', views.serviceman_list_view, name='users'),

    re_path(r'^edit_chain/$', views.edit_service_members_chain_view, name='edit_service_members_chain'),
    re_path(r'^edit_chain/(?P<serviceman_id>\d+)$', views.edit_service_members_chain_view, name='edit_service_members_chain'),

    path('report_filling', views.report_filling_view, name='report_filling'),
    path('final_report', views.return_report_document_view, name='final_report'),


    re_path(r'^search_member/$', views.member_search_view),
    re_path(r'^search_member/(?P<name_format>[-\w]+)$', views.member_search_view),

]


