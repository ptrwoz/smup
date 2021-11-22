from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app.models import Employee
from app.models import Process
from app.models import RuleHasProcess
import datetime

def activityForm(request):
    context = dict()
    if request.user.is_authenticated:
        context['logged'] = 'yes'
        userData = request.user
        employee = Employee.objects.filter(auth_user=userData.id)
        current_datetime = datetime.datetime.now()
        context['current_datetime'] = current_datetime
        #processData = Process.
        if (employee.exists()):
            userData.label = employee[0].name + " " + employee[0].surname
        else:
            userData.label = userData
        context['userData'] = userData
        return render(request, 'activity/activityForm.html', context)
    else:
        context['logged'] = 'no'
        return redirect('home')