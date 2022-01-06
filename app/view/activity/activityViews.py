from django.shortcuts import render, redirect
from app.models import Employee, Rule, AuthUser, RuleHasProcess, RuleHasEmployee
from app.view.auth.auth import authUser
from app.view.static.urls import REDIRECT_HOME_URL, RENDER_ACTIVITY_URL, REDIRECT_ACTIVITIES_URL, RENDER_ACTIVITIES_URL, \
    RENDER_RULE_URL
from datetime import date
from django.db.models import Q
from app.view.user.userViews import getEmployeeToEdit

def updateActivities(request, context, id=''):
    return render(request, RENDER_ACTIVITY_URL, context)

def viewActivity(request, context, id=''):
    context = authUser(request)
    if id == '':
        return redirect(REDIRECT_ACTIVITIES_URL)
    elif id.isnumeric():
        rules = Rule.objects.filter(idrule=int(id))
        if rules.exists():
            processData = []
            ruleHasProcess = RuleHasProcess.objects.filter(rule_id_rule=rules[0].idrule)
            for r in ruleHasProcess:
                processData.append(r.process_idprocess)
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
