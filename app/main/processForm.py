from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app.models import Employee
from app.models import Process

def processForm(request):
    context = dict()
    if request.user.is_authenticated:
        context['logged'] = 'yes'
        userData = request.user
        employee = Employee.objects.filter(auth_user=userData.id)
        #processData = Process.
        if (employee.exists()):
            userData.label = employee[0].name + " " + employee[0].surname
        else:
            userData.label = userData
        context['userData'] = userData
        return render(request, 'auth/profil.html', context)
    else:
        context['logged'] = 'no'
        return redirect('home')