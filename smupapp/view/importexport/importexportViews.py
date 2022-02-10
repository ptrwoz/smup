import os
import re
from datetime import datetime
import pandas as pd
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from openpyxl import load_workbook
from smupapp.models import *
from smupapp.view.auth.auth import authUser
from smupapp.view.process.processViews import initChapterNo, sortDataByChapterNo
from smupapp.view.static.messagesTexts import MESSAGES_IMPORT_NOFILE_ERROR, MESSAGES_IMPORT_SUCCESS
from smupapp.view.static.staticValues import USER_GUEST
from smupapp.view.static.urls import REDIRECT_HOME_URL, RENDER_IMPORT_EXPORT_URL, REDIRECT_IMPORT_EXPORT_URL
from openpyxl.workbook.child import INVALID_TITLE_REGEX

def color(row):
    return ['background-color: red'] * len(row)

def createSumSheet(employee):
    print()
def createEmployeeSheet(employee):
    process = Process.objects.all()
    processData = []
    processNo = []
    tasksRange = []
    process = initChapterNo(process)
    process, idx2 = sortDataByChapterNo(process)
    for p in process:
        processData.append(p.name)
        processNo.append(p.number)
        tasksRange.append('')
    df1 = pd.DataFrame({'Numer': processNo, 'Processy': processData, 'Zakres zadan': tasksRange})

    #df1.set_index('Process', inplace=True)
    #df1.style.apply(color, axis=1)
    return df1

def exportDataBase(id, anonymization = False):
    path = './temp/temp_out/data_%s.xlsx' % id
    employees = Employee.objects.all()
    writer = pd.ExcelWriter(path, engine='xlsxwriter')
    no = 1
    for employee in employees:
        sheet_name = ""
        if anonymization:
            sheet_name = 'Employee_' + str(no)
        else:
            sheet_name = '({}) {}'.format(employee.id_unit.name, employee.name, employee.surname)
            sheet_name = re.sub(INVALID_TITLE_REGEX, '_', sheet_name)
        df1 = createEmployeeSheet(employee)
        df1.to_excel(writer, sheet_name=sheet_name)
        no = no + 1
    writer.save()
    return path

def importFile(request):
    if len(request.FILES) > 0:
        files = request.FILES['myfile']
        now = datetime.now()
        current_time = now.strftime("%m_%d_%Y_%H_%M_%S_%f")
        path = './temp/temp_in/data_%s.xlsx' % str(current_time)
        savedFilePath = default_storage.save(path, ContentFile(files.read()))
        data = load_workbook(savedFilePath)
        messages.info(request, MESSAGES_IMPORT_SUCCESS, extra_tags='info')
        #return render(request, RENDER_IMPORT_EXPORT_URL)
        return redirect(REDIRECT_IMPORT_EXPORT_URL)
    else:
        messages.info(request, MESSAGES_IMPORT_NOFILE_ERROR, extra_tags='error')
        #return render(request, RENDER_IMPORT_EXPORT_URL)
        return redirect(REDIRECT_IMPORT_EXPORT_URL)

def exportFile(request):
    now = datetime.now()
    current_time = now.strftime("%m_%d_%Y_%H_%M_%S_%f")
    path = exportDataBase(str(current_time), False)

    if os.path.exists(path):
        if os.path.exists(path):
            file = open(path, "rb")
            response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=data.xlsx'
            return response

'''def importexportView2(request):
    context = dict()
    if request.user.is_authenticated:
        userData = request.user
        employee = Employee.objects.filter(auth_user=userData.id)
        if employee.exists():
            context['userLabel'] = employee[0].name + " " + employee[0].surname
            context['account'] = str(employee[0].id_employeetype.name)
        else:
            context['userLabel'] = userData
            context['account'] = 'GUEST'
        return render(request, 'importexport/importExport.html', context)
    else:
        context['account'] = 'GUEST'
        return render(request, 'main/home.html', context)
    return redirect(REDIRECT_HOME_URL)'''

def importexportView(request):
    context = authUser(request)
    if context['account'] != USER_GUEST:

        return render(request, RENDER_IMPORT_EXPORT_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)

def importexportManager(request, id = '', operation = ''):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        if request.method == 'POST':
            if len(id) > 0 and operation == '':
                print()
                #return updateRule(request, context, id)
            else:
                print()
                #return saveRule(request, context, id)
        else:
            # active
            if operation == 'active':
                print()
                #return ruleActive(request, id)
            if operation == 'delete':
                print()
                #return deleteRule(request, context, id)
            if operation == 'view':
                print()
                #return viewRule(request, context, id, True)
            if operation == 'clear':
                print()
                #return clearDate(request, context, id)
            else:
                return importexportView(request)
                #return viewRule(request, context, id)

    else:
        return redirect('home')