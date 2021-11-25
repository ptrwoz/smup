from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from app.models import Employee
from app.models import Process
from app.models import RuleHasProcess
import datetime

class UserData:
    name = ""
    surname = ""
    pass

def userView(request, id):
    context = dict()
    foreignUserData = UserData()
    if request.user.is_authenticated:
        userData = request.user
        employee = Employee.objects.filter(auth_user=userData.id)
        role = employee[0].idemployeetype.name
        if employee.exists() :
            context['userLabel'] = employee[0].name + " " + employee[0].surname
            context['account'] = str(employee[0].idemployeetype.name)
            if id != "":
                try:
                    foreignUser = Employee.objects.filter(idunit=int(id))
                    if len(foreignUser) >= 1:
                        foreignUserData.name = foreignUser[0].name
                        foreignUserData.idunit = foreignUser[0].idunit
                        context['unitData'] = foreignUserData
                        context['userData'] = userData
                        return render(request, 'user/user.html', context)
                    elif int(id) == -1:
                        context['unitData'] = foreignUserData
                        context['userData'] = userData
                        return render(request, 'user/user.html', context)
                    else:
                        return redirect('../')
                except:
                    return redirect('../')
                else:
                    return render(request, 'unit/units.html', context)
            else:
                return render(request, 'user/user.html', context)
        else:
            context['userLabel'] = userData
            context['account'] = 'GUEST'
            return redirect('../main/home.html')
    else:
        context['account'] = 'GUEST'
        return redirect('main/home.html')
        #return render(request, 'main/home.html', context)
    #return render(request, 'unit/unit.html', context)
    return redirect('main/home.html')

def usersView(request):
    context = dict()
    if request.user.is_authenticated:
        userData = request.user
        employee = Employee.objects.filter(auth_user=userData.id)
        role = employee[0].idemployeetype.name
        if employee.exists():
            context['userLabel'] = employee[0].name + " " + employee[0].surname
            context['account'] = str(role)
            if(role == 'ADMIN'):
                employeesData = Employee.objects.filter(~Q(auth_user=userData.id))
            elif(role == 'PROCESS MANAGER'):
                employeesData = Employee.objects.filter(Q(idemployeetype__name='MANAGER' or 'USER'))
            elif (role == 'MANAGER'):
                employeesData = Employee.objects.filter(idemployeetype__name='USER')
            context['employeesData'] = employeesData
        else:
            context['userLabel'] = userData
            context['account'] = 'GUEST'
        return render(request, 'user/users.html', context)
    else:
        context['account'] = 'GUEST'
        return redirect('home')
