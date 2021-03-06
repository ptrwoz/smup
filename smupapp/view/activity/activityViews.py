import datetime
import numpy as np
from decimal import Decimal
from django.contrib import messages
from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, QuerySet
from django.shortcuts import render, redirect
from smupapp.models import Employee, Rule, RuleHasEmployee, Activity, RuleHasProcess
from smupapp.view.auth.auth import authUser
from smupapp.view.process.processViews import initChapterNo, sortDataByChapterNo, sortDataByOrder
from smupapp.view.rule.ruleViews import formatRulesMax
from smupapp.view.static.dataModels import DateInformation
from smupapp.view.static.messagesTexts import MESSAGES_OPERATION_SUCCESS
from smupapp.view.static.staticValues import TIMERANGE_DAY, TIMERANGE_WEEK, TIMERANGE_MONTH, PAGEINATION_SIZE
from smupapp.view.static.urls import REDIRECT_HOME_URL, RENDER_ACTIVITY_URL, REDIRECT_ACTIVITIES_URL, \
    RENDER_ACTIVITIES_URL, RENDER_VIEW_ACTIVITY_URL
import math
from datetime import date

class Segment:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
    def getLabel(self):
        if (self.start_date == self.end_date):
            return str(self.start_date)
        else:
            return str(self.start_date) + ' - ' + str(self.end_date)
    def isDay(self):
        if self.start_date == self.end_date:
            return True
        else:
            False

def getSegments(start_date, end_date, interval_delta):

    today = date.today()
    curr_date = start_date
    segments = []
    todayId = -1
    ii = 0
    isWeekends = []
    enable = []
    while (curr_date - interval_delta <= end_date):
        curr_date = start_date + interval_delta
        curr_end_data = curr_date - datetime.timedelta(days=1)

        segment = Segment(start_date, min(curr_end_data,end_date))
        if today >= start_date and today <= curr_end_data:
            todayId = ii
        if segment.start_date.weekday() and segment.isDay:
            isWeekends.append(True)
        else:
            isWeekends.append(False)
        enable.append(True)
        segments.append(segment.getLabel())
        #
        start_date = curr_date
        curr_date = start_date + interval_delta
        ii = ii + 1
    return segments, todayId, isWeekends, enable

def activityExist(user, ruleHasProcess, timeFrom, timeTo):
    activities = Activity.objects.filter(Q(rule_has_process_id_rule_has_process_id = ruleHasProcess.id_rule_has_process) & Q(employee_id_employee__id_employee = user.id) & Q(time_from = timeFrom) & Q(time_to = timeTo))
    if activities.exists():
        return True, activities[0]
    else:
        return False, None

def saveActivity(request, rule, ruleHasProcess, value, activityDate):
    context = authUser(request)
    if context['account'] != 'GUEST':
        user = context['userData']
        employees = Employee.objects.filter(id_employee = user.id)
        if employees.exists()  and rule.exists():
            dateParts = activityDate.split(' - ')
            exist, activity = activityExist(user, ruleHasProcess, dateParts[0], dateParts[1] if len(dateParts) > 1 else dateParts[0])
            if not exist and len(value) > 0:
                activity = Activity()
                activity.time_from = dateParts[0]
                activity.time_to = dateParts[1] if len(dateParts) > 1 else dateParts[0]
                v1 = str(value).split('.')
                if len(v1) == 2:
                    if len(v1[1]) == 1:
                        v1[1] = '0' + v1[1]
                    activity.value = Decimal(v1[0] + '.' + v1[1])
                else:
                    activity.value = value
                #activity.value = float(value)
                activity.time_add = date.today()
                activity.employee_id_employee = employees[0]
                activity.rule_has_process_id_rule_has_process = ruleHasProcess
                activity.save()
            if exist and len(value) > 0:
                v1 = str(value).split('.')
                if len(v1) == 2 :
                    if len(v1[1]) == 1:
                        v1[1] = '0' + v1[1]
                    activity.value = Decimal(v1[0] + '.' + v1[1])
                else:
                    activity.value = value#Decimal(v1[0] + '.' + v1[1])
                activity.save()
            if exist and len(value) == 0:
                activity.delete()
        else:
            return None
    else:
        return redirect(REDIRECT_HOME_URL)

def formatFormData(rows):
    newRows = []
    for r in range(1,len(rows),2):
        if(len(rows[r-1])>0 and len(rows[r]) >0):
            newRows.append(rows[r-1] + '.' + rows[r])
        else:
            newRows.append('')
    return newRows

def checkMaxValue(sumRows, max):
    for sunRow in sumRows:
        if float(sunRow.replace(':','.')) > max:
            return False
    return True
def updateActivities(request, context, rule_id):
    cols = request.POST.getlist('col')
    rows = request.POST.getlist('row')
    rule = Rule.objects.filter(id_rule=rule_id)
    sumRows = rows[-len(cols):]
    rows = rows[0:len(rows)-len(cols)]
    if rule.exists():
        #if not checkMaxValue(sumRows, rule[0].max):
        #    return render(request, RENDER_ACTIVITY_URL, context)
        if rule[0].data_type.id_data_type == 1:
            rows = formatFormData(rows)
            #& ~Q(process_id_process__id_mainprocess=None)
        ruleHasProcess = RuleHasProcess.objects.filter(Q(rule_id_rule=rule_id) ).order_by("process_id_process_id__order")

        colSize = int(len(rows) / (len(cols)))
        rows = np.array(rows)
        #rows = np.transpose(rows)
        rows = rows.reshape((colSize, len(cols)))
        for x in range(len(cols)):
            for y in range(0,colSize):
                #if len(rows[y,x]) > 0:
                saveActivity(request, rule, ruleHasProcess[y], rows[y, x], cols[x])

        messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')

        return editActivity(request, context, id=str(rule_id))
        #return viewActivity(request, id=str(rule_id), userid=context['userData'].id)
        #return render(request, RENDER_ACTIVITY_URL, context)
    else:
        return viewActivity(request, context, id=str(rule_id))
        #return render(request, RENDER_ACTIVITY_URL, context)

def getRelativedeltaFromDateType(timeRangeName):
    if timeRangeName == TIMERANGE_DAY:
        return relativedelta(days=1, months=0, weeks=0)
    elif timeRangeName == TIMERANGE_WEEK:
        return relativedelta(days=0, months=0, weeks=1)
    elif timeRangeName == TIMERANGE_MONTH:
        return relativedelta(days=0, months=1, weeks=0)

def getPagesFromDateType(timeRange):
    if timeRange.name == TIMERANGE_DAY:
        return 7
    elif timeRange.name == TIMERANGE_WEEK:
        return 5
    elif timeRange.name == TIMERANGE_MONTH:
        return 5


def getActivityData(user, dates, rule):
    array = []
    array.append(dates)
    ruleHasProcesses = RuleHasProcess.objects.filter(rule_id_rule=rule.id_rule)
    for date in dates:
        date
    #for rule_has_process in ruleHasProcesses:

    return array

class ActivityDataCounter:
    def __init__(self, activityDatas):
        self.index = 0
        self.activityDatas = activityDatas
        self.currentActivityData = self.activityDatas[self.index]
    @property
    def increment(self):
        if (self.index < len(self.activityDatas)-1):
            self.index = self.index + 1
            self.currentActivityData = self.activityDatas[self.index]
        return ''



def initActivityData(userActivities, processData, activityDatas, data_type):
    newActivityDatas = []
    newActivityDatas.append(activityDatas)
    for p in processData:
        cNewActivityData = []

        for activityData in activityDatas.object_list:
            activity = []
            splitedActivityData = activityData[0].split(' - ')
            if len(splitedActivityData) == 1:
                if len(splitedActivityData[0]) > 0:
                    splitedActivityData[0] = datetime.datetime.strptime(splitedActivityData[0], '%Y-%m-%d').date()
                    activity = userActivities.filter(Q(rule_has_process_id_rule_has_process__process_id_process = p.id_process) & Q(time_from = splitedActivityData[0]) & Q(time_to = splitedActivityData[0]))
                else:
                    splitedActivityData[0] = ''
                    activity = []
            else:
                splitedActivityData[0] = datetime.datetime.strptime(splitedActivityData[0], '%Y-%m-%d').date()
                splitedActivityData[1] = datetime.datetime.strptime(splitedActivityData[1], '%Y-%m-%d').date()
                activity = userActivities.filter(Q(rule_has_process_id_rule_has_process__process_id_process = p.id_process) & Q(time_from = splitedActivityData[0]) & Q(time_to = splitedActivityData[1]))
            if len(activity) > 0:
                if data_type.id_data_type == 1:
                    v1 = format(activity[0].value, '.2f')
                    hmData = str(v1).split('.')
                    cNewActivityData.append(DateInformation(hmData[0],hmData[1],activityData[0], activityData[1],activityData[2]))
                else:
                    cNewActivityData.append(DateInformation(int(activity[0].value), "",activityData[0], activityData[1],activityData[2]))
            else:
                cNewActivityData.append(DateInformation("", "", activityData[0], activityData[1],activityData[2]))
        newActivityDatas.append(cNewActivityData)
    return newActivityDatas


def addEmptyInterval(dayToBack, segments, isWeekends, enable):
    firstDay = datetime.datetime.strptime(segments[0], '%Y-%m-%d').date()
    day = relativedelta(days=1, months=0, weeks=0)
    noDisable = 0
    while firstDay.strftime('%A') != dayToBack:
        firstDay = firstDay - day
        enable.insert(0, False)
        segments.insert(0, str(firstDay))
        isWeekends.insert(0, True)
        noDisable = noDisable + 1
    return segments, isWeekends, enable, noDisable

def viewActivity(request, id='', userid=''):
    context = authUser(request)
    intUserId = int(userid)
    if id == '':
        return redirect(REDIRECT_ACTIVITIES_URL)
    elif id.isnumeric():
        rules = Rule.objects.filter(id_rule=int(id))
        rules = formatRulesMax(rules)
        if rules.exists():
            rule = rules[0]
            start_date = rule.time_from
            end_date = rule.time_to
            #if rule.max_value != None:
            #    rule.max = int(rule.max_value)

            context['ruleData'] = rule

            segments, todayId, isWeekends, enable = getSegments(start_date, end_date,
                                                        getRelativedeltaFromDateType(rule.time_range.name))
            if todayId == -1:
                context['today'] = ''
            else:
                context['today'] = segments[todayId]

            if (rule.time_range.name == TIMERANGE_DAY):
                segments, isWeekends, enable, noDisable = addEmptyInterval('Monday', segments, isWeekends, enable)
                todayId = todayId + noDisable
            paginator = Paginator(list(zip(segments, isWeekends, enable)), getPagesFromDateType(rule.time_range))
            if todayId == -1 or paginator.num_pages == 1:
                currentPage = 1
            else:
                if todayId == 0:
                    todayId = 1
                i = (todayId)

                currentPage = math.ceil((i / len(segments)) * paginator.num_pages)
                if currentPage == 1:
                    currentPage = 1
            page = request.GET.get('page', currentPage)
            try:
                activityData = paginator.page(int(page))
            except PageNotAnInteger:
                activityData = paginator.page(currentPage)
            except EmptyPage:
                activityData = paginator.page(paginator.num_pages)

            activityDatas = []
            activityDatas.append(activityData.object_list)
            processData = []
            ruleHasProcess = RuleHasProcess.objects.filter(Q(rule_id_rule=rule.id_rule)).order_by(
                'process_id_process__order')

            for r in ruleHasProcess:
                p = r.process_id_process
                p.editable = 1
                processData.append(p)
                while p.id_mainprocess != None:
                    # and (not processData[-1].number.find(p.number) == 0)
                    p = p.id_mainprocess
                    # if processData[-1].number.find(p.number) == 0:
                    #    break
                    p.editable = 0
                    processData.append(p)
            processData = list({p.number: p for p in processData}.values())
            # processData.order_by('order')
            # processData = initChapterNo(processData)
            processData, prs = sortDataByOrder(processData)
            context['processData'] = processData

            userActivities = Activity.objects.filter(Q(employee_id_employee__id_employee=intUserId) & Q(
                rule_has_process_id_rule_has_process__rule_id_rule=rule.id_rule))
            activityDatas = initActivityData(userActivities, processData, activityData, rule.data_type)
            formActivityDatas = ActivityDataCounter(activityDatas)
            context['activityPaginator'] = activityData
            context['activityData'] = formActivityDatas

        else:
            return redirect(REDIRECT_ACTIVITIES_URL)

    return render(request, RENDER_VIEW_ACTIVITY_URL, context)

def editActivity(request, context, id=''):

    context = authUser(request)
    if id == '':
        return redirect(REDIRECT_ACTIVITIES_URL)
    elif id.isnumeric():
        rules = Rule.objects.filter(id_rule=int(id))
        rules = formatRulesMax(rules)
        if rules.exists():
            rule = rules[0]
            start_date = rule.time_from
            end_date = rule.time_to

            #if rule.max_value != None:
            #    rule.max = int(rule.max_value)
            context['ruleData'] = rule

            segments, todayId, isWeekends, enable = getSegments(start_date, end_date, getRelativedeltaFromDateType(rule.time_range.name))

            if (rule.time_range.name == TIMERANGE_DAY):
                segments, isWeekends, enable, noDisable = addEmptyInterval('Monday', segments, isWeekends, enable)
                todayId = todayId + noDisable

            if todayId == -1:
                context['today'] = ''
            else:
                context['today'] = segments[todayId]
            paginator = Paginator(list(zip(segments, isWeekends, enable)), getPagesFromDateType(rule.time_range))
            if todayId == -1 or paginator.num_pages == 1:
                currentPage = 1
            else:
                if todayId == 0:
                    todayId = 1
                i = (todayId)

                currentPage = math.ceil((i / len(segments)) * paginator.num_pages)
                if currentPage == 1:
                    currentPage = 1
            page = request.GET.get('page', currentPage)
            try:
                activityData = paginator.page(int(page))
            except PageNotAnInteger:
                activityData = paginator.page(currentPage)
            except EmptyPage:
                activityData = paginator.page(paginator.num_pages)

            activityDatas = []
            activityDatas.append(activityData.object_list)
            processData = []
            ruleHasProcess = RuleHasProcess.objects.filter(Q(rule_id_rule=rule.id_rule)).order_by('process_id_process__order')

            for r in ruleHasProcess:
                p = r.process_id_process
                p.editable = 1
                processData.append(p)
                while p.id_mainprocess != None:
                    #and (not processData[-1].number.find(p.number) == 0)
                    p = p.id_mainprocess
                    #if processData[-1].number.find(p.number) == 0:
                    #    break
                    p.editable = 0
                    processData.append(p)
            processData = list({p.number: p for p in processData}.values())
            #processData.order_by('order')
            #processData = initChapterNo(processData)
            #processData = initChapterNo(processData)
            processData, prs = sortDataByOrder(processData)
            context['processData'] = processData

            userActivities = Activity.objects.filter(Q(employee_id_employee__id_employee = context['userData'].id) & Q(rule_has_process_id_rule_has_process__rule_id_rule = rule.id_rule))
            activityDatas = initActivityData(userActivities, processData, activityData, rule.data_type)
            formActivityDatas = ActivityDataCounter(activityDatas)
            context['activityPaginator'] = activityData
            context['activityData'] = formActivityDatas

        else:
            return redirect(REDIRECT_ACTIVITIES_URL)

    return render(request, RENDER_ACTIVITY_URL, context)

#
#   main function
#
def activitiesManager(request, id='', operation=''):
    context = authUser(request)
    if context['account'] != 'GUEST':
        if request.method == 'POST':
            if len(id) > 0 and operation == '':
                return updateActivities(request, context, int(id))
        else:
            return editActivity(request, context, id)
    else:
        return redirect(REDIRECT_HOME_URL)

def activitiesView(request, field='name', sort='0'):
    context = authUser(request)
    if context['account'] != 'GUEST':
        today = date.today()
        ruleHasEmployees = RuleHasEmployee.objects.filter(Q(employee_id_employee=context['userData'].id))
        rules = []
        for ruleHasEmployee in ruleHasEmployees:
            rule = ruleHasEmployee.rule_id_rule
            if rule.is_active:
                rules.append(rule)
        page = request.GET.get('page', 1)
        paginator = Paginator(rules, PAGEINATION_SIZE)
        try:
            rulesData = paginator.page(page)
        except PageNotAnInteger:
            rulesData = paginator.page(1)
        except EmptyPage:
            rulesData = paginator.page(paginator.num_pages)

        context['rules'] = rulesData

        return render(request, RENDER_ACTIVITIES_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)
