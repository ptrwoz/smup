from datetime import date
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render, redirect
from smupapp.models import Rule, TimeRange, DataType, Employee, Process, RuleHasProcess, Activity, RuleHasEmployee
from smupapp.service.ruleService import ruleActiveById, formatRulesMax, existRuleActivity, getNumberFromDateType, \
    deleteRuleById
from smupapp.view.auth.auth import authUser
from smupapp.view.process.processViews import initChapterNo, initAvailableProcess, sortDataByChapterNo
from smupapp.view.static.messagesTexts import MESSAGES_OPERATION_ERROR, \
    MESSAGES_OPERATION_SUCCESS, MESSAGES_DATA_ERROR, MESSAGES_ACTIVITY_IN_RULE_ERROR, MESSAGES_RULE_NAME_ERROR, \
    MESSAGES_RULE_DATATYPE_ERROR, MESSAGES_RULE_TIMERANGE_ERROR, MESSAGES_RULE_USERS_ERROR, MESSAGES_RULE_PROCESS_ERROR, \
    MESSAGES_RULE_MAX_ERROR, MESSAGES_RULE_DATA_CLEAR_ERROR, MESSAGES_RULE_TIMERANGE_TOO_BIG
from smupapp.view.static.staticValues import PAGEINATION_SIZE
from smupapp.view.static.urls import RENDER_RULE_URL, RENDER_RULES_URL, REDIRECT_HOME_URL, REDIRECT_RULES_URL, \
    REDIRECT_RULE_URL, RENDER_VIEWRULE_URL


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

def initContext(context):
    if (context['account'] == 'ADMIN'):
        employeesData = Employee.objects.all().order_by('surname', 'name')
    elif (context['account'] == 'PROCESS MANAGER'):
        employeesData = Employee.objects.filter(Q(id_employee=context['userData'].id) \
                                                | Q(id_employeetype__name='PROCESS MANAGER') | Q(id_employeetype__name='USER') | Q(id_employeetype__name='MANAGER')).order_by('surname', 'name')
    elif (context['account'] == 'MANAGER'):
        employeesData = Employee.objects.filter(Q(id_employee=context['userData'].id) | Q(id_employeetype__name='MANAGER') | Q(id_employeetype__name='USER')).order_by('surname', 'name')
    elif (context['account'] == 'USER'):
        employeesData = Employee.objects.filter(Q(id_employee=context['userData'].id) | Q(id_employeetype__name='USER')).order_by('surname', 'name')

    context['employeesData'] = employeesData
    context['dataType'] = DataType.objects.all()
    context['timeRange'] = TimeRange.objects.all()
    processes = Process.objects.all().order_by('order')
    processData = initChapterNo(processes)
    processData = initAvailableProcess(processData)
    #processData, prs = sortDataByChapterNo(processData)
    context['processData'] = processData
    return context, processData, processes, processData, employeesData

def initProcessData(processData, static, id = ''):
    checkedProcessData = []
    for p in processData:
        if id == '':
            r = RuleHasProcess.objects.filter(process_id_process=p.id_process)
        else:
            r = RuleHasProcess.objects.filter(rule_id_rule=int(id), process_id_process=p.id_process)
        if r.exists():
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
        checkedProcessData = list({p.number: p for p in checkedProcessData}.values())
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

def clearDate(request, context, id='', userid=''):
    rules = Rule.objects.filter(id_rule=id)
    if rules.exists():
        rule = rules[0]
        if rule.name != request.POST['confirmName']:
            messages.info(request, MESSAGES_RULE_DATA_CLEAR_ERROR, extra_tags='error')
            return redirect(REDIRECT_RULES_URL)
        rulehasprocess = rule.rulehasprocess_set.all()
        if len(userid) == 0:
            activites = Activity.objects.filter(
                Q(rule_has_process_id_rule_has_process__in=rulehasprocess) )
        else:
            activites = Activity.objects.filter(
                Q(rule_has_process_id_rule_has_process__in=rulehasprocess) and Q(employee_id_employee=int(userid)))

        if activites.exists():
            activites.delete()
        messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')
        return redirect(REDIRECT_RULES_URL)
    else:
        messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
        return redirect(REDIRECT_RULES_URL)

def viewRule(request, context, id='', static=False):
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        context, processData, processes, prs, employeesData = initContext(context)
        if id == '':
            return render(request, RENDER_RULE_URL, context)
        elif id.isnumeric():
            checkedEmployeesData = initEmployeesData(employeesData, static, id)
            checkedProcessData = initProcessData(processData, static, id)
            context['processData'] = checkedProcessData
            context['employeesData'] = checkedEmployeesData
        if id == '':
            return render(request, RENDER_RULE_URL, context)
        elif id.isnumeric():
            checkedProcessData = initProcessData(processData, static, id)
            context['processData'] = checkedProcessData

            rules = Rule.objects.filter(id_rule=int(id))
            rules = formatRulesMax(rules)
            if rules.exists():
                rule = rules[0]
                rule.time_from = str(rule.time_from)
                rule.time_to = str(rule.time_to)
                if rule.max_value == None:
                    rule.max_value = ''
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
    result, message = deleteRuleById(int(id))
    if result:
        messages.info(request, message, extra_tags='info')
        return redirect(REDIRECT_RULES_URL)
    else:
        messages.info(request, message, extra_tags='error')
        return redirect(REDIRECT_RULES_URL)

def checkRuleFromForm(request, rule = Rule()):
    name = request.POST.get('ruleName')
    maxValue = request.POST.get('maxValue')
    dataType = request.POST.get('dataType')
    timeRange = request.POST.get('timeRange')
    timeFrom = request.POST.get('timeFrom')
    timeTo = request.POST.get('timeTo')

    mss = None
    rule.name = name
    if len(maxValue) > 0:
        maxValue = maxValue.replace(':', '.')
        try:
            if  float(maxValue) - int(float(maxValue)) >= 60:
                mss =  MESSAGES_RULE_MAX_ERROR
            else:
                rule.max_value = float(maxValue)
        except ValueError:
                mss =  MESSAGES_RULE_MAX_ERROR
    else:
        rule.max_value = None
    rule.time_from = timeFrom
    rule.time_to = timeTo

    rule.is_active = True
    rule.data_type_id = int(dataType)#DataType.objects.filter(id_data_type = int(dataType))[0]
    rule.time_range_id = int(timeRange)#TimeRange.objects.filter(id_time_range = int(timeRange))[0]

    intervalDate = date.fromisoformat(timeTo) - date.fromisoformat(timeFrom)
    timeRangeObject = TimeRange.objects.filter(id_time_range=timeRange)
    if timeRangeObject.exists():
        dayNo = getNumberFromDateType(timeRangeObject[0])
        if (intervalDate.days - dayNo <= 0):
            mss =  MESSAGES_RULE_TIMERANGE_TOO_BIG

    if len(name) <= 2:
        mss = MESSAGES_RULE_NAME_ERROR
    if len(dataType) == 0:
        mss = MESSAGES_RULE_DATATYPE_ERROR
    if len(timeRange) == 0:
        mss = MESSAGES_RULE_TIMERANGE_ERROR
    #    or len(timeFrom) < 10 or len(timeTo) < 10:
    if len(maxValue)>0:
        try:
            float(maxValue)
            if float(maxValue) < 0:
                mss = MESSAGES_DATA_ERROR
            #else:
                #return rule, None
        except ValueError:
            mss = MESSAGES_DATA_ERROR
    return rule, mss

def initPrevForm(request, context, rule):
    context, processData, processes, prs, employeesData = initContext(context)
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
    if rule.max_value == None:
        rule.max_value = ''
    if rule.data_type.id_data_type == 1:
        rule.max_value = str(rule.max_value).replace('.',':')

    return context

def saveRule(request, context):
    rule, me = checkRuleFromForm(request)
    rule.id_rule = None
    if me != None:
        context = initPrevForm(request, context, rule)
        messages.info(request, me, extra_tags='error')
        return render(request, RENDER_RULE_URL, context)
    else:
        context, processData, processes, prs, employeesData = initContext(context)
        if True:
            flag1 = checkProcessInputs(request, processData)
            flag2 = checkEmployeeInputs(request, employeesData)
            if not flag1:
                context = initPrevForm(request, context, rule)
                messages.info(request, MESSAGES_RULE_PROCESS_ERROR, extra_tags='error')
                return render(request, RENDER_RULE_URL, context)
            if not flag2:
                context = initPrevForm(request, context, rule)
                messages.info(request, MESSAGES_RULE_USERS_ERROR, extra_tags='error')
                return render(request, RENDER_RULE_URL, context)
            if flag1 and flag2:
                rule.save()
                for p in processes:
                    value = request.POST.get('check_process_'+ str(p.id_process))
                    ruleHasProcessArray = RuleHasProcess.objects.filter(process_id_process=p.id_process,
                                                                        rule_id_rule=rule.id_rule)
                    if value is not None and not ruleHasProcessArray.exists():
                        ruleHasProcess = RuleHasProcess()
                        ruleHasProcess.process_id_process = p
                        ruleHasProcess.rule_id_rule = rule
                        ruleHasProcess.save()
                    elif value is None and ruleHasProcessArray.exists():
                        ruleHasProcessArray.delete()
                for e in employeesData:
                    value = request.POST.get('check_employee_' + str(e.id_employee))
                    ruleHasEmployeeArray = RuleHasEmployee.objects.filter(employee_id_employee=e.id_employee,
                                                                          rule_id_rule=rule.id_rule)
                    if value is not None and not ruleHasEmployeeArray:
                        ruleHasEmployee = RuleHasEmployee()
                        ruleHasEmployee.rule_id_rule = rule
                        ruleHasEmployee.employee_id_employee = e
                        ruleHasEmployee.save()
                    elif value is None and ruleHasEmployeeArray.exists():
                        ruleHasEmployeeArray.delete()
    messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')
    return redirect(REDIRECT_RULES_URL)

def updateRule(request, context, id=''):

    rules = Rule.objects.filter(id_rule=id)
    if not rules.exists():
        messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
        return redirect(REDIRECT_RULES_URL)
    rule, me = checkRuleFromForm(request, rules[0])
    if existRuleActivity(rule):
        messages.info(request, MESSAGES_ACTIVITY_IN_RULE_ERROR, extra_tags='error')
        context['rule'] = rule
        return viewRule(request, context, id, False)
    if me != None:
        context = initPrevForm(request, context, rule)
        messages.info(request, me, extra_tags='error')
        context['rule'] = rule
        return render(request, RENDER_RULE_URL, context)
    else:
        context, processData, processes, prs, employeesData = initContext(context)
        if True:
        #try:
            flag1 = checkProcessInputs(request, processData)
            flag2 = checkEmployeeInputs(request, employeesData)
            if not flag1:
                context = initPrevForm(request, context, rule)
                messages.info(request, MESSAGES_RULE_PROCESS_ERROR, extra_tags='error')
                return render(request, RENDER_RULE_URL, context)
            if not flag2:
                context = initPrevForm(request, context, rule)
                messages.info(request, MESSAGES_RULE_USERS_ERROR, extra_tags='error')
                return render(request, RENDER_RULE_URL, context)
        try:
            flag1 = checkProcessInputs(request, processData)
            flag2 = checkEmployeeInputs(request, employeesData)
            if flag1 and flag2:
                rule.save()
                for p in processes:
                    value = request.POST.get('check_process_' + str(p.id_process))
                    ruleHasProcessArray = RuleHasProcess.objects.filter(process_id_process=p.id_process,
                                                                        rule_id_rule=rule.id_rule)
                    if value is not None and not ruleHasProcessArray.exists():
                        ruleHasProcess = RuleHasProcess()
                        ruleHasProcess.process_id_process = p
                        ruleHasProcess.rule_id_rule = rule
                        ruleHasProcess.save()
                    elif value is None and ruleHasProcessArray.exists():
                        ruleHasProcessArray.delete()
                for e in employeesData:
                    value = request.POST.get('check_employee_' + str(e.id_employee))
                    ruleHasEmployeeArray = RuleHasEmployee.objects.filter(employee_id_employee=e.id_employee,
                                                                          rule_id_rule=rule.id_rule)
                    if value is not None and not ruleHasEmployeeArray:
                        ruleHasEmployee = RuleHasEmployee()
                        ruleHasEmployee.rule_id_rule = rule
                        ruleHasEmployee.employee_id_employee = e
                        ruleHasEmployee.save()
                    elif value is None and ruleHasEmployeeArray.exists():
                        ruleHasEmployeeArray.delete()
            else:
                context, processData, processes, prs, employeesData = initContext(context)
                processData = initProcessData(processData, False, id)
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
                context['processData'] = processData
                context['rule'] = rule
                messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
                return render(request, RENDER_RULE_URL, context)
        except:
            if id == '':
                rule.delete()
    messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')
    return redirect(REDIRECT_RULES_URL)

def ruleManager(request, id = '', operation = '', userid = ''):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        if request.method == 'POST':
            if operation == 'clear':
                return clearDate(request, context, id, userid)
            if len(id) > 0 and operation == '':
                return updateRule(request, context, id)
            else:
                return saveRule(request, context)
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

#
#   rules view
#
def rulesView(request):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        rules = Rule.objects.all().order_by('name')
        rules = formatRulesMax(rules)
        page = request.GET.get('page', 1)
        paginator = Paginator(rules, PAGEINATION_SIZE)
        #
        try:
            rules = paginator.page(page)
        except PageNotAnInteger:
            rules = paginator.page(1)
        except EmptyPage:
            rules = paginator.page(paginator.num_pages)
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
            if not ruleActiveById(int(id)):
                return redirect(REDIRECT_RULES_URL)
            else:
                return redirect(REDIRECT_RULES_URL)
            rules = Rule.objects.filter(id_rule=int(id))
    else:
        return redirect(REDIRECT_HOME_URL)