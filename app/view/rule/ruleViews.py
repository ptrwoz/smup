from django.shortcuts import render, redirect

from app.models import Rule, TimeRange, DataType
from app.view.auth.auth import authUser

def RuleData():
    name = ""
    max = ""

def ruleView(request, id):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        if id == 0:
            context['rule'] = RuleData()
            return render(request, 'user/user.html', context)
        elif len(id) == 0:
            context['rule'] = RuleData()
            return render(request, 'user/user.html', context)
        elif len(id) > 0 and id.isnumeric():
            ''';;'e = getEmployeeToEdit(id, context['userData'].id, context['account'])
            if e is not None:
                e.login = e.auth_user.username
                e.auth_user = None
                e.password = ""
                context['user'] = e
                return render(request, 'user/user.html', context)
            else:
                return redirect('users')'''
        else:
            return redirect('users')
            rules = Rule.objects.all()
            timeRanges = TimeRange.objects.all()
            dataTypes = DataType.objects.all()
            context['rules'] = rules
            context['timeRanges'] = timeRanges
            context['dataTypes'] = dataTypes
            return render(request, 'rule/rule.html', context)
    else:
        return redirect('home')

def rulesView(request):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        rules = Rule.objects.all()
        context['rules'] = rules
        return render(request, 'rule/rules.html', context)
    else:
        return redirect('home')