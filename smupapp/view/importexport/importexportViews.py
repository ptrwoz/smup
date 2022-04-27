import os
import re
from datetime import datetime
from cryptography.fernet import Fernet
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
from smupapp.view.process.processViews import initChapterNo, sortDataByChapterNo, initAvailableProcess
from smupapp.view.rule.ruleViews import formatRulesMax, initProcessData, initContext
from smupapp.view.static.dataModels import ExcelData
from smupapp.view.static.messagesTexts import MESSAGES_IMPORT_NOFILE_ERROR, MESSAGES_IMPORT_SUCCESS, \
    MESSAGES_TIME_RANGE_EXPORT_ERROR, MESSAGES_NO_RULE_SELECT_ERROR, MESSAGES_NO_EXPORT_FILE_ERROR, \
    MESSAGES_RULES_CONFLICT_ERROR
from smupapp.view.static.staticValues import USER_GUEST, PAGEINATION_SIZE, TIMERANGE_DAY, TIMERANGE_WEEK, \
    TIMERANGE_MONTH
from smupapp.view.static.urls import REDIRECT_HOME_URL, RENDER_IMPORT_EXPORT_URL, REDIRECT_IMPORT_EXPORT_URL
from openpyxl.workbook.child import INVALID_TITLE_REGEX
from datetime import datetime

def color(row):
    return ['background-color: red'] * len(row)


def sumActivity(activities):
    sum = 0
    for activity in activities:
        sum = sum + activity.value
    return sum
def processFormatDataFrame(dataFrame,processData):
    removeIdx = []
    for idx in range(len(processData)):
        if not processData[idx].check:
            removeIdx.append(idx)
    #for nindx in reversed(range(len(removeIdx))):
    dataFrame = dataFrame.drop(dataFrame.index[removeIdx])
    return dataFrame
def formatDataFrame(dataFrame, dataType):
    indexes = dataFrame.index
    data = dataFrame.T.head(1).T.to_numpy()
    #data = data.astype(str)
    for idx in range(len(data) - 1):
        sum = 0
        for idx2 in range(idx,len(data) - 1):
            if indexes[idx] == indexes[idx2][0:len(indexes[idx])]:
                if dataType.id_data_type == 2:
                    sum = sum + data[idx2]
                else:
                    sum = datesSum([sum, data[idx2][0]])
        data[idx] = sum
        '''if dataType.id_data_type == 2:
        else:
            data[idx] = [floatArrayToDate(sum)]'''
    data = data.astype(str)
    if dataType.id_data_type == 1:
        data = floatArrayToDate(data)
    return pd.DataFrame(index=indexes, data=data, columns=dataFrame.columns)

def dateSum(date1, date2):
    val1a = int(date1)
    val1b = round(date1 - int(date1),2)
    #
    val2a = int(date2)
    val2b = round(date2 - int(date2),2)
    sumVal = val1a + val2a
    sumVal2 = val1b + val2b
    if sumVal2 > 0.6:
        sumVal = sumVal + 1
        sumVal2 = round(sumVal2 - 0.6,2)
    return sumVal + sumVal2
def datesSum(dateArray):
    sum = 0
    for value in dateArray:
        sum = dateSum(sum, value)
    return sum
def floatArrayToDate(values):
    for idx in range(len(values)):
        strVal = str(values[idx][0])
        values[idx][0] = strVal.replace('.',':')
        if strVal.find(':') == -1:
            values[idx][0] = strVal + ':00'
    return values
def createSumUnitSheet(dateFrom, dateTo, dataTypes, timeRange, rules, unit, rawProcessData):
    process = Process.objects.all().order_by('-order')
    processData = []
    processNo = []
    tasksRange = []
    process = initChapterNo(process)
    process, idx2 = sortDataByChapterNo(process)
    for p in process:
        processData.append(p.name)
        processNo.append(p.number)
        tasksRange.append('')
    processData.append('')
    tasksRange.append('')
    processNo.append('')
    activityMultiCol = numpy.array(list(zip(processData, tasksRange)))
    ndf = pd.DataFrame(index=processNo, columns=['Processy', 'Zakres zadan'],
                       data=activityMultiCol)
    ndf = processFormatDataFrame(ndf, rawProcessData)
    d1 = {}
    d1[''] = ndf
    dfs = pd.concat(d1, axis=1)
    ruleHasProcess = RuleHasProcess.objects.filter(rule_id_rule__in=rules)

    ruleHasEmployees = RuleHasEmployee.objects.filter(rule_id_rule__in = rules)
    #employees = ruleHasEmployees.employee_id_employee
    employee_id_employee = ruleHasEmployees.values_list('employee_id_employee').distinct()
    employees = Employee.objects.filter(id_employee__in=employee_id_employee)
    if len(unit) == 1:
        employees = employees.filter(id_unit = unit[0].id_unit)
    else:
        employees = employees.filter(id_unit__in=unit.values_list('id_unit'))

    employee_id_employee = employees.values_list('id_employee').distinct()
    Activity.objects.all()
    allActivity = Activity.objects.filter(Q(rule_has_process_id_rule_has_process__in=ruleHasProcess) & Q(employee_id_employee__in=employee_id_employee))
    # for s in segments:
    activityMultiCol = []
    for dt in dataTypes:
        activitySingleCol = []
        for p in process:
            if timeRangeToNumber(timeRange) == 1:
                act = allActivity.filter(rule_has_process_id_rule_has_process__rule_id_rule__data_type__name=dt.name, \
                                         rule_has_process_id_rule_has_process__process_id_process=p.id_process,
                                         time_from__gte=dateFrom, time_to__lte=dateTo)
                if len(act) > 0:
                    activitySingleCol.append(sumActivity(act))
                elif len(act) == 0:
                    activitySingleCol.append(0)

        # activityMultiCol.append(activitySingleCol)
        activitySingleCol = numpy.array(activitySingleCol)
        #activitySingleCol = numpy.flip(activitySingleCol)

        sumActivityValue = ''
        if dt.id_data_type == 2:
            sumActivityValue = numpy.sum(activitySingleCol)
        else:
            sumActivityValue = datesSum(activitySingleCol)
            #sumActivityValue = numpy.sum(activitySingleCol)
        activitySingleCol = numpy.append(activitySingleCol, sumActivityValue)

        activitySingleCol = numpy.array(activitySingleCol)
        # activitySingleCol = numpy.append(activitySingleCol)
        #activitySingleCol = numpy.rot90([activitySingleCol])

        ndf = pd.DataFrame(index=processNo, data=activitySingleCol, columns=[dt.name])

        ndf = formatDataFrame(ndf, dt)
        ndf = processFormatDataFrame(ndf, rawProcessData)
        d1 = {}
        d1['SUM'] = ndf

        d1 = pd.concat(d1, axis=1)


        dfs = pd.concat([dfs, d1], axis=1)

    return dfs

def createSumEmployeeSheet(dateFrom, dateTo, dataTypes, timeRange, rules, unitStatistic):
    process = Process.objects.all().order_by('-order')
    processData = []
    processNo = []
    tasksRange = []
    process = initChapterNo(process)
    process, idx2 = sortDataByChapterNo(process)
    for p in process:
        processData.append(p.name)
        processNo.append(p.number)
        tasksRange.append('')
    processData.append('')
    tasksRange.append('')
    processNo.append('')
    activityMultiCol = numpy.array(list(zip(processData, tasksRange)))
    ndf = pd.DataFrame(index=processNo, columns=['Processy', 'Zakres zadan'],
                       data=activityMultiCol)
    d1 = {}
    d1[''] = ndf
    dfs = pd.concat(d1, axis=1)
    ruleHasProcess = RuleHasProcess.objects.filter(rule_id_rule__in=rules)

    allActivity = Activity.objects.filter(rule_has_process_id_rule_has_process__in=ruleHasProcess)
    #for s in segments:
    activityMultiCol = []
    for dt in dataTypes:
        activitySingleCol = []
        for p in process:
            if timeRangeToNumber(timeRange) == 1:
                act = allActivity.filter(rule_has_process_id_rule_has_process__rule_id_rule__data_type__name=dt.name, \
                                             rule_has_process_id_rule_has_process__process_id_process=p.id_process,
                                             time_from__gte=dateFrom, time_to__lte=dateTo)
                if len(act) > 0:
                    activitySingleCol.append(sumActivity(act))
                elif len(act) == 0:
                    activitySingleCol.append(0)

        #activityMultiCol.append(activitySingleCol)
        activitySingleCol = numpy.array(activitySingleCol)
        activitySingleCol = numpy.flip(activitySingleCol)

        sumActivityValue = ''
        if dt.id_data_type == 2:
            sumActivityValue = numpy.sum(activitySingleCol)
        else:
            sumActivityValue = numpy.sum(activitySingleCol)
        activitySingleCol = numpy.append(activitySingleCol, sumActivityValue)

        activitySingleCol = numpy.array(activitySingleCol)
        #activitySingleCol = numpy.append(activitySingleCol)
        activitySingleCol = numpy.rot90([activitySingleCol])

        ndf = pd.DataFrame(index=processNo, columns=list(dt.name),
                           data=[activitySingleCol])
        d1 = {}
        d1['SUM'] = ndf
        d1 = pd.concat(d1, axis=1)
        dfs = pd.concat([dfs, d1], axis=1)
    return dfs

def createEmployeeSheet(employee, segments, dataTypes, timeRange, rules):
    process = Process.objects.all().order_by('-order')
    processData = []
    processNo = []
    tasksRange = []
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
    ruleHasProcess = RuleHasProcess.objects.filter(rule_id_rule__in=rules)
    allActivity = Activity.objects.filter(rule_has_process_id_rule_has_process__in=ruleHasProcess)
    for s in segments:
        activityMultiCol = []
        for dt in dataTypes:
            activitySingleCol = []
            for p in process:
                if timeRangeToNumber(timeRange) == 1:

                    act = allActivity.filter(rule_has_process_id_rule_has_process__rule_id_rule__data_type__name = dt, \
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
#   sum raport
#
def exportStatisticRaport(formData, employees, writer):
    if len(formData.timeRange) == 0:
        formData.timeRange = getMinTimeRange(formData.rules)

    dataRules = formData.rules.values_list('data_type__name').distinct()

    nDataRules = []
    for dr in dataRules:
        nDataRules.append(dr[0])

    segments, todayId, isWeekends, enables = getSegments(formData.timeFrom, formData.timeTo, getRelativedeltaFromDateType(formData.timeRange))

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
    writer.save()

def exportRaport(formData, writer):
    if len(formData.timeRange) == 0:
        formData.timeRange = getMinTimeRange(formData.rules)

    dataRules = formData.rules.values_list('data_type__id_data_type').distinct()

    nDataRules = []
    for dr in dataRules:
        nDataRules.append(dr[0])
    vDataRules = DataType.objects.filter(id_data_type__in = nDataRules)
    units = Unit.objects.all()
    if formData.unitStatistic == None:
        df1 = createSumUnitSheet(formData.timeFrom, formData.timeTo, vDataRules, formData.timeRange, formData.rules, \
                             units, formData.processData)
        sheetName = 'sum'
        df1.to_excel(writer, sheet_name=sheetName)
        writer.sheets[sheetName].set_row(2, None, None, {'hidden': True})
    else:
        for unit in units:
            df1 = createSumUnitSheet(formData.timeFrom, formData.timeTo, vDataRules, formData.timeRange, formData.rules,\
                             [unit], formData.processData)
        sheetName = '{} sum'.format(unit.name)
        df1.to_excel(writer, sheet_name=sheetName)
        writer.sheets[sheetName].set_row(2, None, None, {'hidden': True})
    writer.save()


def checkRulesCollision(rules):
    for r1 in rules:
        for r2 in rules:
            if r1 != r2:
                if r1.time_from <= r2.time_to and r2.time_from <= r1.time_to and r1.data_type == r2.data_type:
                    return r1, r2, True
    return None, None, False
#
#   generate excel document
#
def exportDataBase(request, id, formData):
    path = './temp/temp_out/data_{}_{}.xlsx'.format(id, formData.docType)
    writer = pd.ExcelWriter(path, engine='xlsxwriter')
    no = 1

    timeFrom = datetime.strptime(formData.timeFrom, "%Y-%m-%d").date()
    timeTo = datetime.strptime(formData.timeTo, "%Y-%m-%d").date()
    formData.timeFrom = timeFrom
    formData.timeTo = timeTo
    r1, r2, result = checkRulesCollision(formData.rules)
    if result:
        return MESSAGES_RULES_CONFLICT_ERROR.format(r1.name,r2.name), False
    if len(formData.rules) == 0:
        return MESSAGES_NO_RULE_SELECT_ERROR, False
    if formData.docType == 'Raport':
        exportRaport(formData, writer)
    else:
        if not checkExportTimeRange(formData.rules, formData.timeRange):
            return MESSAGES_TIME_RANGE_EXPORT_ERROR, False
        employeesHasRule = getExcelEmployees(formData)
        employees = Employee.objects.filter(id_employee__in=employeesHasRule.values('employee_id_employee'))
        exportStatisticRaport(formData, employeesHasRule, writer)

    return path, True

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
        result, success = exportDataBase(request, str(current_time), formData)
        if not success:
            messages.info(request, result, extra_tags='error')
            return redirect(REDIRECT_IMPORT_EXPORT_URL)
        if os.path.exists(result):
            file = open(result, "rb")
            response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=data.xlsx'
            return response
        else:
            messages.info(request, MESSAGES_NO_EXPORT_FILE_ERROR, extra_tags='error')
            return redirect(REDIRECT_IMPORT_EXPORT_URL)
    else:
        redirect(REDIRECT_IMPORT_EXPORT_URL)

def inicheckedProcess(request, processData):
    for p in processData:
        value = request.POST.get('check_process_' + str(p.id_process))
        if value != None:
            p.check = True
        else:
            p.check = False
    return processData
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
    unitStatistic = request.POST.get('unitStatistic')
    anonymizationParam = request.POST.get('anonymizationParam')
    timeMin = request.POST.get('timeMin')
    timeFrom = request.POST.get('timeFrom')
    timeTo = request.POST.get('timeTo')
    checkedRules = []
    processes = Process.objects.all().order_by('order')
    processData = initChapterNo(processes)

    processData = initAvailableProcess(processData)
    processData = inicheckedProcess(request, processData)

    checkedProcess = []
    #processData = initProcessData(processData, False, id)
    for p in processData:
        value = request.POST.get('check_process_' + str(p.id_process))
        if value is not None:
            checkedProcess.append(p.id_process)

    processData1 = processData.filter(id_process__in = checkedProcess)

    rules = Rule.objects.all()
    if rules.exists():
        for rule in rules:
            checkedRule = request.POST.get('rule_id_' + str(rule.id_rule))
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
                 rules1,\
                 processData,\
                 processData1,\
                 unitStatistic)

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

def initProcessData(processData, static, id = ''):
    checkedProcessData = []
    for p in processData:
        if id == '':
            r = RuleHasProcess.objects.filter(process_id_process=p.id_process)
        else:
            r = RuleHasProcess.objects.filter(rule_id_rule=int(id), process_id_process=p.id_process)
        if r.exists():
            if static:
                checkedProcessData.append(p)
                p1 = p
                while p1.id_mainprocess != None:
                    p1 = p1.id_mainprocess
                    checkedProcessData.append(p1)
            p.check = 1
        else:
            p.check = 0
    if static:
        checkedProcessData = list({p.number: p for p in checkedProcessData}.values())
        checkedProcessData = initChapterNo(checkedProcessData)
        checkedProcessData, prs = sortDataByChapterNo(checkedProcessData)
        return checkedProcessData
    return processData

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

        context, processData, processes, prs, employeesData = initContext(context)
        checkedProcessData = initProcessData(processData, False)
        context['processData'] = processData
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
            return importexportView(request)

    else:
        return redirect('home')