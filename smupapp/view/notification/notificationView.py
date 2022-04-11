from datetime import date, datetime

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat
from django.shortcuts import render, redirect

from smupapp.models import RuleHasEmployee, TimeRange, DataType, Activity, RuleHasProcess
from smupapp.view.auth.auth import authUser
from smupapp.view.static.dataModels import NotificationFilterData
from smupapp.view.static.messagesTexts import MESSAGES_ACTIVITY_END, MESSAGES_NO_ACTIVITY, MESSAGES_DELAY, \
    MESSAGES_NO_DELAY
from smupapp.view.static.staticValues import PAGEINATION_SIZE
from smupapp.view.static.urls import RENDER_NOTIFICATIONS_URL, REDIRECT_HOME_URL

def getFilterData(request):
    return NotificationFilterData(request.POST['ruleName'], \
                                  request.POST['userName'], \
                                  request.POST['timeFrom'], \
                                  request.POST['timeTo'],\
                                  request.POST['timeRange'],\
                                  request.POST['dataType'], \
                                  request.POST['delay'])

#def getEmployeeDelay(ruleHasEmployee):

def getActivitiesDelay(today, ruleHasEmployee):
    ruleHasProcess = RuleHasProcess.objects.filter(rule_id_rule = ruleHasEmployee.rule_id_rule)
    #ruleHasEmployee.rule_id_rule
    employee = ruleHasEmployee.employee_id_employee
    today = date.today()
    activities = Activity.objects.filter(Q(employee_id_employee = employee) & \
             Q(rule_has_process_id_rule_has_process__in = ruleHasProcess))
    delays = []
    for activity in activities:
        d = activity.time_to - today
        delays.append(d)
    return delays

class NotificationData:

    def __init__(self):
        self.status = None
        self.intervals = None
        self.days = None
    def __int__(self, status = None, intervals = None, days = None):
        self.status = status
        self.intervals = intervals
        self.days = days

#def isDelay(today, rule):



def addDelay(ruleHasEmployees):
    today = date.today()

    for idx in range(len(ruleHasEmployees)):
        messageData = NotificationData()
        if today > ruleHasEmployees[idx].rule_id_rule.time_to:
            messageData.status = MESSAGES_ACTIVITY_END
            messageData.intervals = ''
            messageData.days = ''
        else:
            no = getActivitiesDelay(today, ruleHasEmployees[idx])
            if len(no) <= 0:
                messageData.status = MESSAGES_NO_ACTIVITY
                messageData.intervals = ''
                messageData.days = ''
            else:
                minDate = min(no)
                if abs(minDate.days) == 0:
                    messageData.status = MESSAGES_NO_DELAY
                    messageData.intervals = ''
                    messageData.days = ''
                else:
                    messageData.status = MESSAGES_DELAY
                    messageData.intervals = ''
                    messageData.days = abs(minDate.days)
        ruleHasEmployees[idx].delay = messageData
    return ruleHasEmployees

def notificationsView(request):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER' or context['account'] == 'USER':

        if len(request.POST) > 0:
            notificationsFilterData = getFilterData(request)
            if context['account'] == 'USER':
                ruleHasEmployee = RuleHasEmployee.objects.filter(employee_id_employee = context['userData'].id)
            else:
                ruleHasEmployee = RuleHasEmployee.objects.all()
            if len(notificationsFilterData.userName) > 0:
                query = ruleHasEmployee.annotate(nameAndSurname=Concat('employee_id_employee__name', Value(' '), 'employee_id_employee__surname', output_field=CharField()))
                ruleHasEmployee = query.filter(Q(nameAndSurname__contains = notificationsFilterData.userName) or\
                                  Q(employee_id_employee__name__contains = notificationsFilterData.userName) or\
                                                              Q(employee_id_employee__surname__contains = notificationsFilterData.userSurname))
            if len(notificationsFilterData.ruleName) > 0:
                    ruleHasEmployee = ruleHasEmployee.filter(Q(rule_id_rule__name__contains = notificationsFilterData.ruleName))

            if len(notificationsFilterData.timeFrom) > 0:
                    ruleHasEmployee = ruleHasEmployee.filter(Q(rule_id_rule__time_from__gte = notificationsFilterData.timeFrom))

            if len(notificationsFilterData.timeTo) > 0:
                    ruleHasEmployee = ruleHasEmployee.filter(Q(rule_id_rule__time_to__lte = notificationsFilterData.timeTo))

            if len(notificationsFilterData.timeRange) > 0:
                ruleHasEmployee = ruleHasEmployee.filter(
                    Q(rule_id_rule__time_range__name__contains=notificationsFilterData.timeRange))

            if len(notificationsFilterData.dataType) > 0:
                ruleHasEmployee = ruleHasEmployee.filter(
                    Q(rule_id_rule__data_type__name__contains=notificationsFilterData.dataType))

            ruleHasEmployee = addDelay(ruleHasEmployee.distinct())
            context['filterData'] = notificationsFilterData

        else:
            if context['account'] == 'USER':
                ruleHasEmployee = RuleHasEmployee.objects.filter(employee_id_employee = context['userData'].id)
            else:
                ruleHasEmployee = RuleHasEmployee.objects.all()
            ruleHasEmployee = addDelay(ruleHasEmployee)
        page = request.GET.get('page', 1)
        paginator = Paginator(ruleHasEmployee, PAGEINATION_SIZE)
        context['timeRange'] = TimeRange.objects.all()
        context['dataType'] = DataType.objects.all()

        try:
            rules = paginator.page(page)
        except PageNotAnInteger:
            rules = paginator.page(1)
        except EmptyPage:
            rules = paginator.page(paginator.num_pages)

        context['notifications'] = rules
        return render(request, RENDER_NOTIFICATIONS_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)

def notificationsManager(request, id = '', operation = '', userid = ''):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        if request.method == 'POST':
            print('')
        else:
            return notificationsView(request, context, id)
            '''# active
            if operation == 'active':
                return ruleActive(request, id)
            if operation == 'delete':
                return deleteRule(request, context, id)
            if operation == 'view':
                return viewRule(request, context, id, True)
            #if operation == 'clear':
            #    return clearDate(request, context, id)
            else:
                return viewRule(request, context, id)'''