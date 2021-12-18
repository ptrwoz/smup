from django.shortcuts import render, redirect

from app.models import Rule, TimeRange, DataType, Employee, Process, RuleHasProcess
from app.view.auth.auth import authUser
from app.view.process.processViews import initChapterNo, initAvailableProcess
from app.view.static.urls import RENDER_RULE_URL, RENDER_RULES_URL, REDIRECT_HOME_URL, REDIRECT_RULES_URL, \
    REDIRECT_RULE_URL, RENDER_UNIT_URL
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect

def RuleData():
    name = ""
    max = ""

def viewRule(request, context, id=''):
    context['rule'] = RuleData()
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        if id == '':
            if (context['account'] == 'ADMIN'):
                employeesData = Employee.objects.filter(~Q(auth_user=context['userData'].id))
            elif (context['account'] == 'PROCESS MANAGER'):
                employeesData = Employee.objects.filter(
                    Q(idemployeetype__name='USER') | Q(idemployeetype__name='MANAGER'))
            elif (context['account'] == 'MANAGER'):
                employeesData = Employee.objects.filter(idemployeetype__name='USER')
            context['employeesData'] = employeesData
            context['dataType'] = DataType.objects.all()
            context['timeRange'] = TimeRange.objects.all()
            processData = Process.objects.all()
            processData = initChapterNo(processData)
            processData = initAvailableProcess(processData)
            context['processData'] = processData
            return render(request, RENDER_RULE_URL, context)
        elif id.isnumeric():
            rules = Rule.objects.filter(idrule=int(id))
            if rules.exists():
                rule = rules[0]
                context['unitData'] = rule
                return render(request, REDIRECT_RULE_URL, context)
        else:
            return redirect(REDIRECT_RULE_URL)
    else:
        return redirect(REDIRECT_HOME_URL)

def saveRole(request, context, id =''):
    name = request.POST.get('ruleName')
    maxValue = request.POST.get('maxValue')
    dataType = request.POST.get('dataType')
    timeRange = request.POST.get('timeRange')
    timeFrom = request.POST.get('timeFrom')
    timeTo = request.POST.get('timeTo')
    roleValue = request.POST.get('roleValue')
    rule = Rule()
    rule.idrule = None
    rule.name = name
    rule.max = maxValue
    rule.timefrom = timeFrom
    rule.timeto = timeTo
    rule.data_type_iddata_type = DataType.objects.filter(iddata_type = int(dataType))[0]
    rule.time_range_idtime_range = TimeRange.objects.filter(idtime_range = int(timeRange))[0]
    rule.employee_idemployee = Employee.objects.filter(idemployee = int(roleValue))[0]
    processes = Process.objects.all()
    rule.save()
    for p in processes:
        value = request.POST.get('check_'+ str(p.idprocess))
        if value is not None:
            ruleHasProcess = RuleHasProcess()
            ruleHasProcess.process_idprocess = p.idprocess
            ruleHasProcess.id_rule_has_process = rule.idrule
            ruleHasProcess.save()

    print()
def updateRule(request, context, id):
    print()
def ruleManager(request, id = '', operation = ''):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        if request.method == 'POST':
            if len(id) > 0 and operation == '':
                return updateRule(request, context, id)
            else:
                saveRole(request, context, id)
                return None
        else:
            # active
            if operation == 'active':
                return ruleActive(request, id)
            if id == 0:
                context['rule'] = RuleData()
                if (context['account'] == 'ADMIN'):
                    employeesData = Employee.objects.filter(~Q(auth_user=context['userData'].id))
                elif (context['account'] == 'PROCESS MANAGER'):
                    employeesData = Employee.objects.filter(
                        Q(idemployeetype__name='USER') | Q(idemployeetype__name='MANAGER'))
                elif (context['account'] == 'MANAGER'):
                    employeesData = Employee.objects.filter(idemployeetype__name='USER')
                context['employeesData'] = employeesData
                context['dataType'] = DataType.objects.all()
                context['timeRange'] = TimeRange.objects.all()
                processData = Process.objects.all()
                processData = initChapterNo(processData)
                processData = initAvailableProcess(processData)
                context['processData'] = processData
                return render(request, RENDER_RULE_URL, context)
            else:
                return viewRule(request, context, id)

    else:
        return redirect('home')

def rulesView(request):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        rules = Rule.objects.all()
        context['rules'] = rules
        return render(request, RENDER_RULES_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)
#
#   user change active
#
def ruleActive(request, id=''):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        if len(id) > 0:
            rules = Rule.objects.filter(idrule=int(id))
            if rules is not None:
                r = rules[0]
                if r.isactive == 1:
                    r.isactive = 0
                else:
                    r.isactive = 1
                r.save()
                return redirect(REDIRECT_RULES_URL)
            else:
                return redirect(REDIRECT_RULES_URL)
    else:
        return redirect(REDIRECT_HOME_URL)