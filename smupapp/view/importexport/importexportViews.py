import os
import re
from datetime import datetime
import pandas as pd
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import QuerySet, Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from openpyxl import load_workbook
from smupapp.models import *
from smupapp.view.activity.activityViews import getSegments, getRelativedeltaFromDateType
from smupapp.view.auth.auth import authUser
from smupapp.view.process.processViews import initChapterNo, sortDataByChapterNo
from smupapp.view.rule.ruleViews import formatRulesMax
from smupapp.view.static.dataModels import ExcelData
from smupapp.view.static.messagesTexts import MESSAGES_IMPORT_NOFILE_ERROR, MESSAGES_IMPORT_SUCCESS
from smupapp.view.static.staticValues import USER_GUEST, PAGEINATION_SIZE, TIMERANGE_DAY, TIMERANGE_WEEK, \
    TIMERANGE_MONTH
from smupapp.view.static.urls import REDIRECT_HOME_URL, RENDER_IMPORT_EXPORT_URL, REDIRECT_IMPORT_EXPORT_URL
from openpyxl.workbook.child import INVALID_TITLE_REGEX
from datetime import datetime

def color(row):
    return ['background-color: red'] * len(row)

def createSumSheet(employee):
    print()
def createEmployeeSheet(employee, segments):
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

'''def getEmployerActivities(employee,  ,formData):

    Unit.objects.filter(Q(is_active=1))

    Activity.objects.filter(Q(time_from=[formData.timeFrom, formData.timeTo]) | \
                            Q(employee_id_employee = employee.id_employee) | \
                            )'''


#
#   get unique employees from rules
#
def getExcelEmployees(formData = None):
    userQuery = None
    for rule in formData.rules:
        ruleHasEmployee = RuleHasEmployee.objects.filter(rule_id_rule = rule.id_rule)
        if userQuery == None:
            userQuery = ruleHasEmployee
        else:
            userQuery = userQuery | ruleHasEmployee
    userQuery = userQuery.distinct().order_by('id_unit__name')
    return userQuery

def getExcelEmployees(formData = None):
    userQuery = None
    for rule in formData.rules:
        ruleHasEmployee = RuleHasEmployee.objects.filter(rule_id_rule = rule.id_rule)
        if userQuery == None:
            userQuery = ruleHasEmployee
        else:
            userQuery = userQuery | ruleHasEmployee
    userQuery = userQuery.distinct().order_by('id_unit__name')
    return userQuery

def getExcelEmployees(formData = None):
    userQuery = None
    for rule in formData.rules:
        ruleHasEmployee = RuleHasEmployee.objects.filter(rule_id_rule = rule.id_rule)
        if userQuery == None:
            userQuery = ruleHasEmployee
        else:
            userQuery = userQuery | ruleHasEmployee
    userQuery = userQuery.distinct().order_by('id_unit__name')
    return userQuery

def getExcelEmployees(formData = None):
    userQuery = None
    for rule in formData.rules:
        ruleHasEmployee = RuleHasEmployee.objects.filter(rule_id_rule = rule.id_rule)
        if userQuery == None:
            userQuery = ruleHasEmployee
        else:
            userQuery = userQuery | ruleHasEmployee
    userQuery = userQuery.distinct().order_by('id_unit__name')
    return userQuery

def getExcelEmployees(formData = None):
    userQuery = None
    for rule in formData.rules:
        ruleHasEmployee = RuleHasEmployee.objects.filter(rule_id_rule = rule.id_rule)
        if userQuery == None:
            userQuery = ruleHasEmployee
        else:
            userQuery = userQuery | ruleHasEmployee
    userQuery = userQuery.distinct().order_by('id_unit__name')
    return userQuery

def getExcelEmployees(formData = None):
    userQuery = None
    for rule in formData.rules:
        ruleHasEmployee = RuleHasEmployee.objects.filter(rule_id_rule = rule.id_rule)
        if userQuery == None:
            userQuery = ruleHasEmployee
        else:
            userQuery = userQuery | ruleHasEmployee
    userQuery = userQuery.distinct().order_by('id_unit__name')
    return userQuery

def getExcelEmployees(formData = None):
    userQuery = None
    for rule in formData.rules:
        ruleHasEmployee = RuleHasEmployee.objects.filter(rule_id_rule = rule.id_rule)
        if userQuery == None:
            userQuery = ruleHasEmployee
        else:
            userQuery = userQuery | ruleHasEmployee
    userQuery = userQuery.distinct().order_by('id_unit__name')
    return userQuery

def getExcelEmployees(formData = None):
    userQuery = None
    for rule in formData.rules:
        ruleHasEmployee = RuleHasEmployee.objects.filter(rule_id_rule = rule.id_rule)
        if userQuery == None:
            userQuery = ruleHasEmployee
        else:
            userQuery = userQuery | ruleHasEmployee
    userQuery = userQuery.distinct().order_by('id_unit__name')
    return userQuery

def getExcelEmployees(formData = None):
    userQuery = None
    for rule in formData.rules:
        ruleHasEmployee = RuleHasEmployee.objects.filter(rule_id_rule = rule.id_rule)
        if userQuery == None:
            userQuery = ruleHasEmployee
        else:
            userQuery = userQuery | ruleHasEmployee
    #userQuery = userQuery.distinct().objects
    #filter(employee_id_employee)

    #    order_by('id_unit__name')
    return userQuery


#
#   generate excel document
#
def exportDataBase(id, formData):
    path = './temp/temp_out/data_%s.xlsx' % id
    employees = Employee.objects.all()
    writer = pd.ExcelWriter(path, engine='xlsxwriter')
    no = 1

    timeFrom =  datetime.strptime(formData.timeFrom, "%Y-%m-%d").date()
    timeTo = datetime.strptime(formData.timeTo, "%Y-%m-%d").date()

    segments, todayId, isWeekends = getSegments(timeFrom, timeTo, getRelativedeltaFromDateType(formData.timeRange))

    employees = getExcelEmployees(formData)
    for employee in employees:

        ruleHasEmployees = RuleHasEmployee.objects.filter(Q(employee_id_employee=employee) & \
                                       Q(rule_id_rule=formData.rules))

        sheet_name = ""
        if formData.anonymizationParam:
            sheet_name = 'Employee_' + str(no)
        else:
            sheet_name = '({}) {}'.format(employee.id_unit.name, employee.name, employee.surname)
            sheet_name = re.sub(INVALID_TITLE_REGEX, '_', sheet_name)
        df1 = createEmployeeSheet(employee, segments)
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
    formData = getDataFromForm(request)
    if checkExportData(formData):
        now = datetime.now()
        current_time = now.strftime("%m_%d_%Y_%H_%M_%S_%f")
        path = exportDataBase(str(current_time), formData)

        if os.path.exists(path):
            if os.path.exists(path):
                file = open(path, "rb")
                response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename=data.xlsx'
                return response
    else:
        redirect(REDIRECT_IMPORT_EXPORT_URL)

def getDataFromForm(request):
    docType = request.POST.get('docType')
    averageParam = request.POST.get('averageParam')
    dominantParam = request.POST.get('dominantParam')
    varianceParam = request.POST.get('varianceParam')
    maximumParam = request.POST.get('maximumParam')
    minimumParam = request.POST.get('minimumParam')
    standardDeviationParam = request.POST.get('standardDeviationParam')
    typicalRangeOfVolatilityParam = request.POST.get('typicalRangeOfVolatilityParam')
    timeMinParam = request.POST.get('timeMinParam')
    timeRange = request.POST.get('timeRange')
    anonymizationParam = request.POST.get('anonymizationParam')
    timeMin = request.POST.get('timeMin')
    timeFrom = request.POST.get('timeFrom')
    timeTo = request.POST.get('timeTo')
    checkedRules = []
    rules = Rule.objects.all()
    if rules.exists():
        for rule in rules:
            checkedRule = request.POST.get('id_' + str(rule.id_rule))
            if checkedRule == 'on':
                checkedRules.append(rule)
    else:
        return None
    return ExcelData(docType, \
                 averageParam, \
                 dominantParam, \
                 varianceParam, \
                 maximumParam, \
                 minimumParam, \
                 standardDeviationParam, \
                 typicalRangeOfVolatilityParam, \
                 timeMinParam, \
                 timeRange,
                 anonymizationParam,
                 timeMin,\
                 timeFrom, \
                 timeTo, \
                 timeRange, \
                 rules)

def getTimeRangeNumber(timeRangeName):
    if timeRangeName == TIMERANGE_DAY:
        return 1
    elif timeRangeName == TIMERANGE_WEEK:
        return 2
    elif timeRangeName == TIMERANGE_MONTH:
        return 3

def checkExportData(formData):
    #for rule in formData.rules:
    #    if rule
    return True

#def initExport():



def importexportView(request):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER' or context['account'] == 'USER':
        context['timeRange'] = TimeRange.objects.all()
        rules = Rule.objects.all().order_by('name')
        rules = formatRulesMax(rules)
        page = request.GET.get('page', 1)

        starting_day_of_current_year = datetime.now().date().replace(month=1, day=1)
        ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)

        context['excelData'] = ExcelData(timeFrom = str(starting_day_of_current_year), \
                                         timeTo = str(ending_day_of_current_year))
        paginator = Paginator(rules, PAGEINATION_SIZE)
        try:
            rules = paginator.page(page)
        except PageNotAnInteger:
            rules = paginator.page(1)
        except EmptyPage:
            rules = paginator.page(paginator.num_pages)
        context['rules'] = rules
        return render(request, RENDER_IMPORT_EXPORT_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)

def importexportManager(request, id = '', operation = ''):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER' or context['account'] == 'USER':
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