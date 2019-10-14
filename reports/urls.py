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
from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [

    path('', views.report_home_view, name='index'),

    path('form', views.dyn_form_view, name='form'),
    path('test_1', views.test_form_view_1, name='test_page'),
    path('generate', views.report_generate_view_1, name='generate'),


    path('users_1', views.users_1_view, name='users'),
    path('user_reports', views.user_reports_view, name='user_reports')

]

