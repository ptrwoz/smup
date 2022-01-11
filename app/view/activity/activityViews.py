import datetime

from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from app.models import Employee, Rule, AuthUser, RuleHasProcess, RuleHasEmployee
from app.view.auth.auth import authUser
from app.view.process.processViews import initChapterNo, sortDataByChapterNo
from app.view.static.staticStrings import TIMERANGE_DAY, TIMERANGE_WEEK, TIMERANGE_MONTH
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
    curr_date = start_date
    segments = []

    while (curr_date <= end_date):
        curr_date = start_date + interval_delta
        segment = Segment(start_date, curr_date - datetime.timedelta(days=1))
        segments.append(segment.getLabel())
        start_date = curr_date
        curr_date = start_date + interval_delta
    return segments

def updateActivities(request, context, id=''):
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
        return 3

def viewActivity(request, context, id=''):
    context = authUser(request)
    if id == '':
        return redirect(REDIRECT_ACTIVITIES_URL)
    elif id.isnumeric():

        #start_date = datetime.datetime(2022, 1, 1)
        #end_date = datetime.datetime(2022, 4, 1)
        rules = Rule.objects.filter(id_rule=int(id))
        if rules.exists():
            start_date = rules[0].time_from
            end_date = rules[0].time_to
            segments = get_segments(start_date, end_date, getRelativedeltaFromDateType(rules[0].time_range))

            page = request.GET.get('page', 1)

            paginator = Paginator(segments, getPagesFromDateType(rules[0].time_range))
            try:
                activityData = paginator.page(page)
            except PageNotAnInteger:
                activityData = paginator.page(1)
            except EmptyPage:
                activityData = paginator.page(paginator.num_pages)
            context['activityData'] = activityData

            processData = []
            ruleHasProcess = RuleHasProcess.objects.filter(rule_id_rule=rules[0].id_rule)
            for r in ruleHasProcess:
                p = r.process_id_process
                processData.append(p)
                while p.id_mainprocess != None:
                    p = p.id_mainprocess
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
                return updateActivities(request, context, id)
                #return updateActive(request, context, id)
        else:
            return viewActivity(request, context, id)


def activitiesView(request, field='name', sort='0'):
    context = authUser(request)
    if context['account'] != 'GUEST':
        #id = AuthUser.objects.filter()
        today = date.today()
        todayDate = today.strftime("%Y-%m-%d")
        ruleHasEmployees = RuleHasEmployee.objects.filter(Q(employee_id_employee=context['userData'].id))
        rules = []
        for ruleHasEmployee in ruleHasEmployees:
            rules.append(ruleHasEmployee.rule_id_rule)
            #= Rule.objects.filter(Q(employee_id_employee_id=context['userData'].id))
    # & Q(timeto__lte=todayDate)
        context['rules'] = rules
        return render(request, RENDER_ACTIVITIES_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)

'''def activityView(request):
    context = authUser(request)
    if context['account'] != 'GUEST':
        # save and update
        if request.method == 'POST':
            print()
        elif request.method == 'DELETE':
            print()
        # view user
        else:
            rules = Rule.objects.filter(employee_idemployee=context['userData'].id)
            context['rules'] = rules
            return render(request, RENDER_ACTIVITY_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)'''
