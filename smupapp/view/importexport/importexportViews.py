import os
import re
from datetime import datetime

import numpy
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
from smupapp.view.static.messagesTexts import MESSAGES_IMPORT_NOFILE_ERROR, MESSAGES_IMPORT_SUCCESS, \
    MESSAGES_TIME_RANGE_EXPORT_ERROR
from smupapp.view.static.staticValues import USER_GUEST, PAGEINATION_SIZE, TIMERANGE_DAY, TIMERANGE_WEEK, \
    TIMERANGE_MONTH
from smupapp.view.static.urls import REDIRECT_HOME_URL, RENDER_IMPORT_EXPORT_URL, REDIRECT_IMPORT_EXPORT_URL
from openpyxl.workbook.child import INVALID_TITLE_REGEX
from datetime import datetime

def color(row):
    return ['background-color: red'] * len(row)

def createSumSheet(employee):
    print()
def createEmployeeSheet(employee, segments, dataTypes, timeRange, rules):
    process = Process.objects.all().order_by('-order')
    processData = []
    #processData.append('')
    processNo = []
    #processNo.append('')
    tasksRange = []
    #tasksRange.append('')
    process = initChapterNo(process)
    process, idx2 = sortDataByChapterNo(process)
    for p in process:
        processData.append(p.name)
        processNo.append(p.number)
        tasksRange.append('')

    activityMultiCol = numpy.array(list(zip(processData, tasksRange)))
    ndf = pd.DataFrame(index=processNo, columns=['Processy', 'Zakres zadan'],
                       data=activityMultiCol)
    d1 = {}
    d1[''] = ndf
    dfs = pd.concat(d1, axis=1)

    #dfs = pd.DataFrame()
    for s in segments:
        activityMultiCol = []
        for dt in dataTypes:
            activitySingleCol = []
            for p in process:
                if timeRangeToNumber(timeRange) == 1:
                    ruleHasProcess = RuleHasProcess.objects.filter(rule_id_rule__in = rules)
                    act = Activity.objects.filter(rule_has_process_id_rule_has_process__in = ruleHasProcess, \
                                                  rule_has_process_id_rule_has_process__process_id_process = p.id_process,time_from=s, time_to=s, employee_id_employee=employee.id_employee)
                    if len(act) > 0:
                        activitySingleCol.append(act[0].value)
                    elif len(act) == 0:
                        activitySingleCol.append(0)
                else:
                    x = s.split(' - ')
                    ruleHasProcess = RuleHasProcess.objects.filter(rule_id_rule__in = rules,process_id_process=p.id_process)
                    act = Activity.objects.filter(rule_has_process_id_rule_has_process__in=ruleHasProcess, \
                                                  rule_has_process_id_rule_has_process__process_id_process=p.id_process,
                                                  time_from=x[0], time_to=x[1], employee_id_employee=employee.id_employee)
                    if len(act) > 0:
                        print()
                    elif len(act) == 0:
                        activitySingleCol.append(0)

            activityMultiCol.append(activitySingleCol)
        activityMultiCol = numpy.array(activityMultiCol)
        activityMultiCol = numpy.rot90(activityMultiCol)

        ndf = pd.DataFrame(index = processNo, columns=list(dataTypes),
                              data=activityMultiCol)
        d1 = {}
        d1[s] = ndf
        d1 = pd.concat(d1, axis=1)

        dfs = pd.concat([dfs, d1], axis=1)
    return dfs

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
    #userQuery = userQuery.distinct().objects
    #filter(employee_id_employee)

    #    order_by('id_unit__name')
    return userQuery

def timeRangeToNumber(timeRange):
    if timeRange == TIMERANGE_DAY:
        return 1
    elif timeRange == TIMERANGE_WEEK:
        return 7
    elif timeRange == TIMERANGE_MONTH:
        return 31

def isDivedTimeRange(tr1, tr2):
    if timeRangeToNumber(tr1) <= timeRangeToNumber(tr2):
        return True
    else:
        return False

def getMinTimeRange(rules):
    minTimeRange = rules[0].time_range.name
    #for rule in rules:
    #    rule
    return minTimeRange

def checkExportTimeRange(rules, timeRange):
    if len(timeRange) == 0:
        return True
    for rule in rules:
        if not timeRangeToNumber(rule.time_range.name) <= timeRangeToNumber(timeRange): #not isDivedTimeRange(rule.time_range.name,timeRange):
            return False
    return True
#
#   generate excel document
#
def exportDataBase(id, formData):
    path = './temp/temp_out/data_%s.xlsx' % id
    #employees = Employee.objects.all()
    writer = pd.ExcelWriter(path, engine='xlsxwriter')
    no = 1

    timeFrom =  datetime.strptime(formData.timeFrom, "%Y-%m-%d").date()
    timeTo = datetime.strptime(formData.timeTo, "%Y-%m-%d").date()

    employeesHasRule = getExcelEmployees(formData)

    employees = Employee.objects.filter(id_employee__in = employeesHasRule.values('employee_id_employee'))

    if len(formData.rules) == 0:
        return None
    if len(formData.timeRange) == 0:
        formData.timeRange = getMinTimeRange(formData.rules)
    if not checkExportTimeRange(formData.rules, formData.timeRange):
        return None

    dataRules = formData.rules.values_list('data_type__name').distinct()

    nDataRules = []
    for dr in dataRules:
        nDataRules.append(dr[0])

    segments, todayId, isWeekends = getSegments(timeFrom, timeTo, getRelativedeltaFromDateType(formData.timeRange))

    for employee in employees:
        sheet_name = ""
        if formData.anonymizationParam:
            sheet_name = 'Employee_' + str(no)
        else:
            sheet_name = '({}) {}'.format(employee.id_unit.name, employee.name, employee.surname)
            sheet_name = re.sub(INVALID_TITLE_REGEX, '_', sheet_name)

        df1 = createEmployeeSheet(employee, segments, nDataRules, formData.timeRange, formData.rules)
        df1.to_excel(writer, sheet_name=sheet_name)
        writer.sheets[sheet_name].set_row(2, None, None, {'hidden': True})
        no = no + 1
    #writer.delete_rows(row[0].row, 1)
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

        if path == None:
            messages.info(request, MESSAGES_TIME_RANGE_EXPORT_ERROR, extra_tags='error')
            return redirect(REDIRECT_IMPORT_EXPORT_URL)
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
                checkedRules.append(rule.id_rule)
        rules1 = rules.filter(id_rule__in = checkedRules)
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
                 rules1)

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

from cryptography.fernet import Fernet

def backup(request):
    now = datetime.now()
    current_time = now.strftime("%m_%d_%Y_%H_%M_%S_%f")
    path = 'backup/{}.json.'.format(current_time)
    os.system("python -Xutf8 manage.py dumpdata --natural-foreign --exclude=auth.permission --exclude=contenttypes --indent=4 > {}".format(path))
    if os.path.exists(path):
        if os.path.exists(path):
            with open('key.key', 'rb') as keyFile:
                key = keyFile.read()
            with open(path, 'rb') as f:
                data = f.read()
            fernet = Fernet(key)
            encrypted = fernet.encrypt(data)
            with open(path, 'wb') as f:
                f.write(encrypted)
            f.close()
            keyFile.close()
            with open(path, 'rb') as f:
                data = f.read()
            response = HttpResponse(data,
                                content_type='application/txt')
            response['Content-Disposition'] = 'attachment; filename=backup_{}.json'.format(current_time)

            return response
    else:
        redirect(REDIRECT_IMPORT_EXPORT_URL)


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