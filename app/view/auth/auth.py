from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app.models import Employee


class UserData:
    id = ""
    name = ""
    surname = ""
    login = ""
    password = ""
    unit = ""
    role = ""
    pass

def authUser(request):
    context = dict()
    userData = UserData()
    if request.user.is_authenticated:
        userName = request.user
        employee = Employee.objects.filter(auth_user=userName.id)
        if employee.exists():
            userData.id = employee[0].idemployee
            userData.name = str(employee[0].name)
            userData.surname = str(employee[0].surname)
            userData.unit = str(employee[0].idunit.name)
            userData.role = str(employee[0].idemployeetype.name)
            userData.login = str(employee[0].auth_user.username)
            context['userLabel'] = employee[0].name + " " + employee[0].surname
            context['account'] = str(employee[0].idemployeetype.name)
            context['userData'] = userData
        else:
            context['userLabel'] = userName
            context['account'] = 'GUEST'
    else:
        context['account'] = 'GUEST'
    return context
