from django.shortcuts import render, redirect

from app.models import Rule, TimeRange, DataType, Employee, Process, RuleHasProcess, Activity, RuleHasEmployee
from app.view.auth.auth import authUser
from app.view.process.processViews import initChapterNo, initAvailableProcess, checkChaptersNo, sortDataByChapterNo
from app.view.static.dataModels import RuleData
from app.view.static.messagesTexts import MESSAGES_ACTIVITYINRULE_ERROR, MESSAGES_OPERATION_ERROR, \
    MESSAGES_OPERATION_SUCCESS, MESSAGES_DATA_ERROR
from app.view.static.urls import RENDER_RULE_URL, RENDER_RULES_URL, REDIRECT_HOME_URL, REDIRECT_RULES_URL, \
    REDIRECT_RULE_URL, RENDER_UNIT_URL, RENDER_VIEWRULE_URL
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect

def checkProcessInputs(request, processes, tag = 'check_process_'):
    flag = False
    for p in processes:
        value = request.POST.get(tag + str(p.id_process))
        if value is not None:
            flag = True
            break
    return flag

def checkEmployeeInputs(request, employees, tag = 'check_employee_'):
    flag = False
    for e in employees:
        value = request.POST.get(tag + str(e.id_employee))
        if value is not None:
            flag = True
            break
    return flag

def initForm(request, context, id=''):
    if (context['account'] == 'ADMIN'):
        employeesData = Employee.objects.all().order_by('surname', 'name')
    elif (context['account'] == 'PROCESS MANAGER'):
        employeesData = Employee.objects.filter(Q(id_employee=context['userData'].id) |
                                                Q(id_employeetype__name='USER') | Q(id_employeetype__name='MANAGER')).order_by('surname', 'name')
    elif (context['account'] == 'MANAGER'):
        employeesData = Employee.objects.filter(Q(id_employee=context['userData'].id) | Q(id_employeetype__name='USER')).order_by('surname', 'name')
    context['employeesData'] = employeesData
    context['dataType'] = DataType.objects.all()
    context['timeRange'] = TimeRange.objects.all()
    processes = Process.objects.all()
    processData = initChapterNo(processes)
    processData = initAvailableProcess(processData)
    processData, prs = sortDataByChapterNo(processData)
    context['processData'] = processData
    return context, processData, processes, prs, employeesData

def showRule(request, context, id=''):
    context['rule'] = RuleData()
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        context, processData, processes, prs, employeesData = initForm(request, context, id)
        if not checkChaptersNo(prs):
            return viewRule(request, context, id)
        if id == '':
            return render(request, RENDER_RULE_URL, context)

def initProcessData(processData, static, id = ''):
    checkedProcessData = []
    for p in processData:
        if RuleHasProcess.objects.filter(rule_id_rule=int(id), process_id_process=p.id_process).exists():
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
        checkedProcessData = list({p.name: p for p in checkedProcessData}.values())
        checkedProcessData = initChapterNo(checkedProcessData)
        checkedProcessData, prs = sortDataByChapterNo(checkedProcessData)
        return checkedProcessData
    return processData

def initEmployeesData(employeesData, static, id = ''):
    checkedEmployeesData = []
    for e in employeesData:
        if RuleHasEmployee.objects.filter(rule_id_rule=int(id),
                                          employee_id_employee=e.id_employee).exists():
            if static:
                checkedEmployeesData.append(e)
            e.check = 1
        else:
            e.check = 0
    if static:
        return checkedEmployeesData
    else:
        return employeesData

def viewRule(request, context, id='', static=False):
    context['rule'] = RuleData()
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        context, processData, processes, prs, employeesData = initForm(request, context, id)
        if not checkChaptersNo(prs):
            return viewRule(request, context, id)
        if id == '':
            return render(request, RENDER_RULE_URL, context)
        elif id.isnumeric():
            checkedEmployeesData = initEmployeesData(employeesData, static, id)
            context['employeesData'] = checkedEmployeesData
        if id == '':
            return render(request, RENDER_RULE_URL, context)
        elif id.isnumeric():
            checkedProcessData = initProcessData(processData, static, id)
            context['processData'] = checkedProcessData

            rules = Rule.objects.filter(id_rule=int(id))
            if rules.exists():
                rule = rules[0]
                rule.time_from = str(rule.time_from)
                rule.time_to = str(rule.time_to)
                context['rule'] = rule
                if static:
                    return render(request, RENDER_VIEWRULE_URL, context)
                else:
                    return render(request, RENDER_RULE_URL, context)
        else:
            return redirect(REDIRECT_RULE_URL)
    else:
        return redirect(REDIRECT_HOME_URL)

def deleteRule(request, context, id=''):
    rules = Rule.objects.filter(id_rule=id)
    if rules.exists():
        try:
            ruleHasProcessSet = RuleHasProcess.objects.filter(rule_id_rule=rules[0].id_rule)
            if existRuleActivity(rules[0]):
                messages.info(request, MESSAGES_ACTIVITYINRULE_ERROR, extra_tags='error')
                return redirect(REDIRECT_RULES_URL)

            '''for ruleHasProcess in ruleHasProcessSet:
                activities = Activity.objects.filter(rule_has_process_id_rule_has_process=ruleHasProcess.id_rule_has_process)
                if(len(activities) > 0):
                    messages.info(request, MESSAGES_ACTIVITYINRULE_ERROR, extra_tags='error')
                    return redirect(REDIRECT_RULES_URL)'''
            for ruleHasProcess in ruleHasProcessSet:
                ruleHasProcess.delete()

            ruleHasEmployeeSet = RuleHasEmployee.objects.filter(rule_id_rule=rules[0].id_rule)
            for ruleHasEmployee in ruleHasEmployeeSet:
                ruleHasEmployee.delete()
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
    #rule = Rule()
    rule.name = name
    rule.max = maxValue
    rule.time_from = timeFrom
    rule.time_to = timeTo
    rule.is_active = True
    rule.data_type_id = int(dataType)#DataType.objects.filter(id_data_type = int(dataType))[0]
    rule.time_range_id = int(timeRange)#TimeRange.objects.filter(id_time_range = int(timeRange))[0]

    if len(name) <= 2 or len(dataType) == 0 or len(timeRange) == 0 or len(timeFrom) < 10 or len(timeTo) < 10:
        return rule, MESSAGES_DATA_ERROR
    try:
        float(maxValue)
        if float(maxValue) < 0:
            return rule, MESSAGES_DATA_ERROR
        else:
            return rule, None
    except ValueError:
        return rule, MESSAGES_DATA_ERROR

    if maxValue.isdigit():
        if int(maxValue) < 0:
            return rule, MESSAGES_DATA_ERROR
        else:
            return rule, None
    else:
        return rule, MESSAGES_DATA_ERROR

def saveRule(request, context, id =''):
    rule, me = checkRuleFromForm(request)
    if me != None:
        messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
        context, processData, processes, prs, employeesData = initForm(request, context)

        for p in processData:
            value = request.POST.get('check_process_' + str(p.id_process))
            if value is not None:
                p.check = 1
            else:
                p.check = 0
        for e in employeesData:
            value = request.POST.get('check_employee_' + str(e.id_employee))
            if value is not None:
                e.check = 1
            else:
                e.check = 0

        context['employeesData'] = employeesData
        context['processData'] = processData
        context['rule'] = rule
        return render(request, RENDER_RULE_URL, context)
    else:
        context, processData, processes, prs, employeesData = initForm(request, context)
        try:
            flag1 = checkProcessInputs(request, processData)
            flag2 = checkEmployeeInputs(request, employeesData)
            if flag1 and flag2:
                rule.save()
                for p in processes:
                    value = request.POST.get('check_process_'+ str(p.id_process))
                    if value is not None:
                        ruleHasProcess = RuleHasProcess()
                        ruleHasProcess.process_id_process = p
                        ruleHasProcess.rule_id_rule = rule
                        #ruleHasProcess.id_rule_has_process = None
                        ruleHasProcess.save()
                for e in employeesData:
                    value = request.POST.get('check_employee_' + str(e.id_employee))
                    if value is not None:
                        ruleHasEmployee = RuleHasEmployee()
                        ruleHasEmployee.rule_id_rule = rule
                        ruleHasEmployee.employee_id_employee = e
                        ruleHasEmployee.save()
            else:
                messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
                context, processData, processes, prs, employees = initForm(request, context)
                processData = initProcessData(processData, False, id)
                context['processData'] = processData
                context['rule'] = rule
                return render(request, RENDER_RULE_URL, context)
        except:
            rule.delete()
    return redirect(REDIRECT_RULES_URL)

def existRuleActivity(rule):
    ruleHasProcessSet = RuleHasProcess.objects.filter(rule_id_rule=rule.id_rule)
    for ruleHasProcess in ruleHasProcessSet:
        activities = Activity.objects.filter(rule_has_process_id_rule_has_process=ruleHasProcess.id_rule_has_process)
        if (len(activities) > 0):
            return True
    return False

def updateRule(request, context, id=''):

    rules = Rule.objects.filter(id_rule=id)
    if rules.exists():
        try:
            if existRuleActivity(rules[0]):
                messages.info(request, MESSAGES_ACTIVITYINRULE_ERROR, extra_tags='error')
                return redirect(REDIRECT_RULES_URL)
        except:
            messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
            return redirect(REDIRECT_RULES_URL)

    rule, me = checkRuleFromForm(request, rules[0])
    if me != None:
        messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
        context['rule'] = rule
        return render(request, RENDER_RULE_URL, context)
    else:
        context, processData, processes, prs, employeesData = initForm(request, context)
        try:
            flag1 = checkProcessInputs(request, processData)
            flag2 = checkEmployeeInputs(request, employeesData)
            if flag1 and flag2:
                rule.save()
                for p in processes:
                    value = request.POST.get('check_process_' + str(p.id_process))
                    if value is not None:
                        ruleHasProcess = RuleHasProcess()
                        ruleHasProcess.process_id_process = p
                        ruleHasProcess.rule_id_rule = rule
                        ruleHasProcess.save()
                    else:
                        ruleHasProcessArray = RuleHasProcess.objects.filter(process_id_process = p.id_process, rule_id_rule = rule.id_rule)
                        if ruleHasProcessArray.exists():
                            ruleHasProcessArray.delete()
                for e in employeesData:
                    value = request.POST.get('check_employee_' + str(e.id_employee))
                    if value is not None:
                        ruleHasEmployee = RuleHasEmployee()
                        ruleHasEmployee.rule_id_rule = rule
                        ruleHasEmployee.employee_id_employee = e
                        ruleHasEmployee.save()
                    else:
                        ruleHasEmployeeArray = RuleHasEmployee.objects.filter(employee_id_employee = e.id_employee, rule_id_rule = rule.id_rule)
                        if ruleHasEmployeeArray.exists():
                            ruleHasEmployeeArray.delete()
            else:
                messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
                context, processData, processes, prs, employeesData = initForm(request, context)
                for p in processData:
                    value = request.POST.get('check_process_' + str(p.id_process))
                    if value is not None:
                        p.check = 1
                    else:
                        p.check = 0

                for e in employeesData:
                    value = request.POST.get('check_employee_' + str(p.id_employee))
                    if value is not None:
                        e.check = 1
                    else:
                        e.check = 0

                context['employeesData'] = employeesData
                context['processData'] = processData
                context['rule'] = rule
                return render(request, RENDER_RULE_URL, context)
        except:
            if id == '':
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
            if operation == 'view':
                return viewRule(request, context, id, True)
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
            rules = Rule.objects.filter(id_rule=int(id))
            if rules is not None:
                r = rules[0]
                if r.is_active == 1:
                    r.is_active = 0
                else:
                    r.is_active = 1
                r.save()
                return redirect(REDIRECT_RULES_URL)
            else:
                return redirect(REDIRECT_RULES_URL)
    else:
        return redirect(REDIRECT_HOME_URL)