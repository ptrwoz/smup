import os
from datetime import datetime
import pandas as pd
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from openpyxl import load_workbook
from app.models import *
from app.view.process.processViews import initChapterNo, sortDataByChapterNo


def color(row):
    return ['background-color: red'] * len(row)

def createEmployeeSheet(employee):
    process = Process.objects.all()
    processData = []
    processNo = []
    process = initChapterNo(process)
    process, idx2 = sortDataByChapterNo(process)
    for p in process:
        processData.append(p.name)
        processNo.append(p.no)
    df1 = pd.DataFrame({'No': processNo, 'Process': processData })

    #df1.set_index('Process', inplace=True)
    #df1.style.apply(color, axis=1)
    return df1

def exportDataBase(id, anonymization = False):
    path = './temp/temp_out/data_%s.xlsx' % id
    employees = Employee.objects.all()
    writer = pd.ExcelWriter(path, engine='xlsxwriter')
    no = 1
    for e in employees:
        sheet_name = ""
        if anonymization:
            sheet_name = 'Employee_' + str(no) + ' Unit_'
        else:
            sheet_name = e.name + " " + e.surname + ' Unit_'
        df1 = createEmployeeSheet(e)
        df1.to_excel(writer, sheet_name=sheet_name)
        no = no + 1
    writer.save()
    return path

def importFile(request):
    files = request.FILES['myfile']
    now = datetime.now()
    current_time = now.strftime("%m_%d_%Y_%H_%M_%S_%f")
    path = './temp/temp_in/data_%s.xlsx' % str(current_time)
    savedFilePath = default_storage.save(path, ContentFile(files.read()))
    data = load_workbook(savedFilePath)
    print()

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

def importexportView(request):
    context = dict()
    if request.user.is_authenticated:
        userData = request.user
        employee = Employee.objects.filter(auth_user=userData.id)
        if employee.exists():
            context['userLabel'] = employee[0].name + " " + employee[0].surname
            context['account'] = str(employee[0].idemployeetype.name)
        else:
            context['userLabel'] = userData
            context['account'] = 'GUEST'
        return render(request, 'importexport/importExport.html', context)
    else:
        context['account'] = 'GUEST'
        return render(request, 'main/home.html', context)
    return redirect('importExport')
