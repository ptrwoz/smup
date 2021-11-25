from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app.models import Employee
from app.models import Process
'''def processViewProcessing(processData):
    for p in processData:
        if
    return processData'''
def processView(request):
    context = dict()
    if request.user.is_authenticated:
        context['logged'] = 'yes'
        userData = request.user
        employee = Employee.objects.filter(auth_user=userData.id)
        if (employee.exists()):
            userData.email = userData.email
            userData.label = employee[0].name + " " + employee[0].surname
            userData.idemployeeType = employee[0].idemployeetype.name
            userData.unit = employee[0].idunit.name
        else:
            userData.label = userData
        context['userData'] = userData
        processData = Process.objects.all()
        #viewProcessData = processViewProcessing(processData)
        #context['processData'] = viewProcessData
        return render(request, 'process/process.html', context)
    else:
        context['logged'] = 'no'
        return redirect('home')
