from django.shortcuts import render, redirect

from app.models import Rule, TimeRange, DataType, Employee, Process
from app.view.auth.auth import authUser
from app.view.process.processViews import initChapterNo, initAvailableProcess
from app.view.static.urls import RENDER_RULE_URL, RENDER_RULES_URL, REDIRECT_HOME_URL
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect

def RuleData():
    name = ""
    max = ""

def ruleView(request, id = 0, operation = ''):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        if request.method == 'GET':
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
                rules = Rule.objects.all()
                timeRanges = TimeRange.objects.all()
                dataTypes = DataType.objects.all()
                context['rules'] = rules
                context['timeRanges'] = timeRanges
                context['dataTypes'] = dataTypes
                return render(request, 'rule/rule.html', context)
        elif request.method == 'POST':
            if id == 0 > 0 and operation == '':
                #return updateUser(request, context, id)
                print()
            elif len(id) > 0 and operation == 'delete':
                #return deleteUser(request, context, id)
                print()
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

def ruleActive(request, id=''):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        '''if len(id) > 0:
            e = getEmployeeToEdit(id, context['userData'].id, context['account'])
            if e is not None:
                if e.isactive == 1:
                    e.isactive = 0
                else:
                    e.isactive = 1
                e.save()
                return redirect(REDIRECT_USERS_URL)
            else:
                return redirect(REDIRECT_USERS_URL)'''
    else:
        return redirect(REDIRECT_HOME_URL)