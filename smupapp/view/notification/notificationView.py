from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render, redirect

from smupapp.models import RuleHasEmployee, TimeRange, DataType
from smupapp.view.auth.auth import authUser
from smupapp.view.static.dataModels import NotificationFilterData
from smupapp.view.static.staticValues import PAGEINATION_SIZE
from smupapp.view.static.urls import RENDER_NOTIFICATIONS_URL, REDIRECT_HOME_URL

def getFilterData(request):
    return NotificationFilterData(request.POST['ruleName'], \
                                  request.POST['userName'], \
                                  request.POST['timeFrom'], \
                                  request.POST['timeTo'],\
                                  request.POST['timeRange'],\
                                  request.POST['dataType'])

def notificationsView(request):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        if len(request.POST) > 0:
            notificationsFilterData = getFilterData(request)
            ruleHasEmployee = RuleHasEmployee.objects.all()
            if len(notificationsFilterData.userName) > 0:
                ruleHasEmployee = ruleHasEmployee.filter(Q(Q(employee_id_employee__name__contains = notificationsFilterData.userName) or\
                                                              Q(employee_id_employee__surname__contains = notificationsFilterData.userName)))
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


            context['filterData'] = notificationsFilterData
        else:
            ruleHasEmployee = RuleHasEmployee.objects.all()
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