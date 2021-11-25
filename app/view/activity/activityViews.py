from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app.models import Employee
from app.models import Process
from app.models import RuleHasProcess
import datetime

def activityView(request):

    context = dict()
    if request.user.is_authenticated:
        userData = request.user
        employee = Employee.objects.filter(auth_user=userData.id)
        if employee.exists():
            context['userLabel'] = employee[0].name + " " + employee[0].surname
            context['account'] = str(employee[0].idemployeetype.name)
        else:
            context['userLabel'] = userData
            context['account'] = 'GUEST'
        return render(request, 'activity/activity.html', context)
    else:
        context['account'] = 'GUEST'
        return redirect('home')
