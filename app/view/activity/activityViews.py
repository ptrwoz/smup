import datetime
import numpy as np
from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from app.models import Employee, Rule, AuthUser, RuleHasEmployee, Activity, RuleHasProcess
from app.view.auth.auth import authUser
from app.view.process.processViews import initChapterNo, sortDataByChapterNo
from app.view.static.staticValues import TIMERANGE_DAY, TIMERANGE_WEEK, TIMERANGE_MONTH
from app.view.static.urls import REDIRECT_HOME_URL, RENDER_ACTIVITY_URL, REDIRECT_ACTIVITIES_URL, RENDER_ACTIVITIES_URL, \
    RENDER_RULE_URL
from datetime import date
from django.db.models import Q
from app.view.user.userViews import getEmployeeToEdit

class Segment:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
    def getLabel(self):
        if (self.start_date == self.end_date):
            return str(self.start_date)
        else:
            return str(self.start_date) + ' - ' + str(self.end_date)

def get_segments(start_date, end_date, interval_delta):

    today = date.today()
    curr_date = start_date
    segments = []
    todayId = -1
    ii = 0
    while (curr_date <= end_date):
        curr_date = start_date + interval_delta
        curr_end_data = curr_date - datetime.timedelta(days=1)
        segment = Segment(start_date, curr_end_data)
        if today >= start_date and today <= curr_end_data:
            todayId = ii
        segments.append(segment.getLabel())
        start_date = curr_date
        curr_date = start_date + interval_delta
        ii = ii + 1
    return segments, todayId

#def dataRowFormat(cols, rows):
#    for col

def activityExist(ruleHasProcess, timeFrom, timeTo):
    activities = Activity.objects.filter(Q(rule_has_process_id_rule_has_process= ruleHasProcess) & Q(time_from = timeFrom) & Q(time_to = timeTo))
    if activities.exists():
        return True
    else:
        return False

def saveActivity(rule, ruleHasProcess, value, activityDate):

    if rule.exists() and len(value) > 1:
        rule = rule[0]
        if rule.data_type.id_data_type == 1:
            value = float(value.replace(':','.'))
        dateParts = activityDate.split(' - ')
        if not activityExist(ruleHasProcess, dateParts[0], dateParts[1]):
            activity = Activity()
            activity.time_from = dateParts[0]
            if rule.data_type.id_data_type == 0:
                activity.time_to = dateParts[0]
            else:
                activity.time_to = dateParts[1]
            activity.value = value
            activity.time_add = date.today()
            activity.rule_has_process_id_rule_has_process = ruleHasProcess
            activity.save()
    else:
        return None
def formatFormData(rows):
    newRows = []
    for r in range(1,len(rows),2):
        newRows.append(rows[r-1] + ':' + rows[r])
    return newRows
def updateActivities(request, context, rule_id):
    cols = request.POST.getlist('col')
    rows = request.POST.getlist('row')
    rule = Rule.objects.filter(id_rule=rule_id)
    if rule.exists():
        if rule[0].data_type.id_data_type == 1:
            rows = formatFormData(rows)

        ruleHasProcess = RuleHasProcess.objects.filter(rule_id_rule=rule_id)
        colSize = int(len(rows) / len(cols))
        rows = np.array(rows)
        rows = np.transpose(rows)
        rows = rows.reshape((colSize, len(cols)))
        for x in range(len(cols)):
            for y in range(0,colSize):
                if len(rows[y,x]) > 0:
                    saveActivity(rule, ruleHasProcess[x], rows[y, x], cols[x])
        return render(request, RENDER_ACTIVITY_URL, context)
    else:
        return render(request, RENDER_ACTIVITY_URL, context)

def getRelativedeltaFromDateType(timeRange):
    if timeRange.name == TIMERANGE_DAY:
        return relativedelta(days=1, months=0, weeks=0)
    elif timeRange.name == TIMERANGE_WEEK:
        return relativedelta(days=0, months=0, weeks=1)
    elif timeRange.name == TIMERANGE_MONTH:
        return relativedelta(days=0, months=1, weeks=0)

def getPagesFromDateType(timeRange):
    if timeRange.name == TIMERANGE_DAY:
        return 7
    elif timeRange.name == TIMERANGE_WEEK:
        return 5
    elif timeRange.name == TIMERANGE_MONTH:
        return 5
#def getActivityData(dates, rule_has_processes):
#    for rule_has_process in rule_has_processes:

def viewActivity(request, context, id=''):
    context = authUser(request)
    if id == '':
        return redirect(REDIRECT_ACTIVITIES_URL)
    elif id.isnumeric():

        rules = Rule.objects.filter(id_rule=int(id))
        if rules.exists():
            rule = rules[0]
            start_date = rule.time_from
            end_date = rule.time_to
            rule.max = int(rules[0].max)
            context['ruleData'] = rule

            segments, todayId = get_segments(start_date, end_date, getRelativedeltaFromDateType(rule.time_range))
            if todayId == -1:
                context['today'] = ''
            else:
                context['today'] = segments[todayId]
            paginator = Paginator(segments, getPagesFromDateType(rule.time_range))
            if todayId == -1 or paginator.num_pages == 1:
                currentPage = 1
            else:
                i = (todayId - 1)
                currentPage = i % (paginator.num_pages)
                if currentPage == 0:
                    currentPage = 1
            page = request.GET.get('page', currentPage)
            allActivityData = []
            try:
                activityDatas = paginator.page(page)
            except PageNotAnInteger:
                activityDatas = paginator.page(currentPage)
            except EmptyPage:
                activityDatas = paginator.page(paginator.num_pages)
            #allActivityData.append(activityDatas)
            #for activityData in activityDatas:

            context['activityData'] = activityDatas

            processData = []
            ruleHasProcess = RuleHasProcess.objects.filter(rule_id_rule=rule.id_rule)
            for r in ruleHasProcess:
                p = r.process_id_process
                p.editable = 1
                processData.append(p)
                while p.id_mainprocess != None:
                    p = p.id_mainprocess
                    p.editable = 0
                    processData.append(p)
                processData = list({p.name: p for p in processData}.values())
            processData = initChapterNo(processData)
            processData, prs = sortDataByChapterNo(processData)
            context['processData'] = processData


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
            return viewActivity(request, context, id)


def activitiesView(request, field='name', sort='0'):
    context = authUser(request)
    if context['account'] != 'GUEST':
        today = date.today()
        #todayDate = today.strftime("%Y-%m-%d")
        ruleHasEmployees = RuleHasEmployee.objects.filter(Q(employee_id_employee=context['userData'].id))
        rules = []
        for ruleHasEmployee in ruleHasEmployees:
            rule = ruleHasEmployee.rule_id_rule
            if rule.is_active:
                rules.append(rule)
        context['rules'] = rules
        return render(request, RENDER_ACTIVITIES_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)
