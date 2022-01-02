from django.shortcuts import render, redirect

from app.models import Rule, TimeRange, DataType, Employee, Process, RuleHasProcess, Activity
from app.view.auth.auth import authUser
from app.view.process.processViews import initChapterNo, initAvailableProcess, checkChaptersNo, sortDataByChapterNo
from app.view.static.dataModels import RuleData
from app.view.static.messagesTexts import MESSAGES_ACTIVITYINRULE_ERROR, MESSAGES_OPERATION_ERROR, \
    MESSAGES_OPERATION_SUCCESS, MESSAGES_DATA_ERROR
from app.view.static.urls import RENDER_RULE_URL, RENDER_RULES_URL, REDIRECT_HOME_URL, REDIRECT_RULES_URL, \
    REDIRECT_RULE_URL, RENDER_UNIT_URL
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect


def viewRule(request, context, id=''):
    context['rule'] = RuleData()
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
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
        processData, prs = sortDataByChapterNo(processData)
        if checkChaptersNo(prs) == False:
            return viewRule(request, context, id)
        context['processData'] = processData
        if id == '':
            return render(request, RENDER_RULE_URL, context)
        elif id.isnumeric():
            for p in processData:
                if RuleHasProcess.objects.filter(rule_idrule=int(id), process_idprocess=p.idprocess).exists():
                    p.check = 1
                else:
                    p.check = 0
            rules = Rule.objects.filter(idrule=int(id))
            if rules.exists():
                rule = rules[0]
                context['rule'] = rule
                return render(request, RENDER_RULE_URL, context)
        else:
            return redirect(REDIRECT_RULE_URL)
    else:
        return redirect(REDIRECT_HOME_URL)

def deleteRule(request, context, id=''):
    rules = Rule.objects.filter(idrule=id)
    if rules.exists():
        try:
            ruleHasProcessSet = RuleHasProcess.objects.filter(rule_idrule=rules[0].idrule)
            for ruleHasProcess in ruleHasProcessSet:
                activities = Activity.objects.filter(rule_has_process_id_rule_has_process=ruleHasProcess.id_rule_has_process)
                if(len(activities) > 0):
                    messages.info(request, MESSAGES_ACTIVITYINRULE_ERROR, extra_tags='error')
                    return redirect(REDIRECT_RULES_URL)
            for ruleHasProcess in ruleHasProcessSet:
                ruleHasProcess.delete()
            rules[0].delete()
            messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')
            return redirect(REDIRECT_RULES_URL)
        except:
            messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
            return redirect(REDIRECT_RULES_URL)

def checkRuleFromForm(request, rule = Rule()):
    name = request.POST.get('ruleName')
    maxValue = request.POST.get('maxValue')
    dataType = request.POST.get('dataType')
    timeRange = request.POST.get('timeRange')
    timeFrom = request.POST.get('timeFrom')
    timeTo = request.POST.get('timeTo')
    roleValue = request.POST.get('roleValue')
    #rule = Rule()
    rule.name = name
    rule.max = maxValue
    rule.timefrom = timeFrom
    rule.timeto = timeTo
    rule.data_type_iddata_type = DataType.objects.filter(iddata_type = int(dataType))[0]
    rule.time_range_idtime_range = TimeRange.objects.filter(idtime_range = int(timeRange))[0]
    rule.employee_idemployee = Employee.objects.filter(idemployee = int(roleValue))[0]

    if len(name) <= 2 or len(dataType) == 0 or len(timeRange) == 0 or len(timeFrom) < 10 or len(timeTo) <= 10 or len(roleValue) == 2:
        return rule, MESSAGES_DATA_ERROR
    if not maxValue.isnumeric():
        if int(maxValue) < 0:
            return rule, MESSAGES_DATA_ERROR
    return rule, None

def saveRule(request, context, id =''):
    rule, me = checkRuleFromForm(request)
    if me != None:
        messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
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
        processData, prs = sortDataByChapterNo(processData)
        for p in processData:
            value = request.POST.get('check_' + str(p.idprocess))
            if value is not None:
                p.check = 1
            else:
                p.check = 0
        context['processData'] = processData
        context['rule'] = rule
        return render(request, RENDER_RULE_URL, context)
    else:
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
        processData, prs = sortDataByChapterNo(processData)
        context['processData'] = processData
        processes = Process.objects.all()
        try:
            flag = False
            for p in processes:
                value = request.POST.get('check_'+ str(p.idprocess))
                if value is not None:
                    flag = True
                    break
            if flag:
                rule.save()
                for p in processes:
                    value = request.POST.get('check_'+ str(p.idprocess))
                    if value is not None:
                        ruleHasProcess = RuleHasProcess()
                        ruleHasProcess.process_idprocess = p
                        ruleHasProcess.rule_idrule = rule
                        ruleHasProcess.id_rule_has_process = None
                        ruleHasProcess.save()
        except:
            rule.delete()
    return redirect(REDIRECT_RULES_URL)

def updateRule(request, context, id=''):

    rules = Rule.objects.filter(idrule=id)
    if rules.exists():
        try:
            ruleHasProcessSet = RuleHasProcess.objects.filter(rule_idrule=rules[0].idrule)
            for ruleHasProcess in ruleHasProcessSet:
                activities = Activity.objects.filter(rule_has_process_id_rule_has_process=ruleHasProcess.id_rule_has_process)
                if(len(activities) > 0):
                    messages.info(request, MESSAGES_ACTIVITYINRULE_ERROR, extra_tags='error')
                    return redirect(REDIRECT_RULES_URL)
            for ruleHasProcess in ruleHasProcessSet:
                ruleHasProcess.delete()
        except:
            messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
            return redirect(REDIRECT_RULES_URL)

    rule, me = checkRuleFromForm(request, rules[0])
    if me != None:
        messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
        context['rule'] = rule
        return render(request, RENDER_RULE_URL, context)
    else:
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
        processData, prs = sortDataByChapterNo(processData)
        context['processData'] = processData
        processes = Process.objects.all()
        try:
            flag = False
            for p in processes:
                value = request.POST.get('check_' + str(p.idprocess))
                if value is not None:
                    flag = True
                    break
            if flag:
                rule.save()
                for p in processes:
                    value = request.POST.get('check_' + str(p.idprocess))
                    if value is not None:
                        ruleHasProcess = RuleHasProcess()
                        ruleHasProcess.process_idprocess = p
                        ruleHasProcess.rule_idrule = rule
                        ruleHasProcess.id_rule_has_process = None
                        ruleHasProcess.save()
        except:
            rule.delete()
    return redirect(REDIRECT_RULES_URL)

def ruleManager(request, id = '', operation = ''):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        if request.method == 'POST':
            if len(id) > 0 and operation == '':
                return updateRule(request, context, id)
            else:
                return saveRule(request, context, id)
        else:
            # active
            if operation == 'active':
                return ruleActive(request, id)
            if operation == 'delete':
                return deleteRule(request, context, id)
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