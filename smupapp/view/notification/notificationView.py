from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect

from smupapp.models import RuleHasEmployee, TimeRange
from smupapp.view.auth.auth import authUser
from smupapp.view.static.staticValues import PAGEINATION_SIZE
from smupapp.view.static.urls import RENDER_NOTIFICATIONS_URL, REDIRECT_HOME_URL


def notificationsView(request):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        ruleHasEmployee = RuleHasEmployee.objects.all()
        page = request.GET.get('page', 1)
        paginator = Paginator(ruleHasEmployee, PAGEINATION_SIZE)
        context['timeRange'] = TimeRange.objects.all()
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