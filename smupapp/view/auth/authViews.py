from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from smupapp.models import Employee
from smupapp.view.auth.auth import authUser
from smupapp.view.static.messagesTexts import MESSAGES_LOGIN_ERROR
from smupapp.view.static.staticValues import USER_GUEST, USER_ACCOUNT, LOGIN_USERNAME, PASSWORD_USERNAME
from smupapp.view.static.urls import RENDER_PROFIL_URL, REDIRECT_HOME_URL, RENDER_LOGIN_URL, RENDER_CHANGE_PASSWORD_URL, \
    RENDER_USER_URL
from smupapp.view.user.userViews import getEmployeeToEdit


def profilUserView(request):
    context = authUser(request)
    if context[USER_ACCOUNT] != USER_GUEST:
        return render(request, RENDER_PROFIL_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)

def changePasswordView(request):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        employees = Employee.objects.filter(id_employee=int(context['userData'].id))
        if employees.exists():
            employee = employees[0]
        if employee is not None:
            employee.login = employee.auth_user.username
            employee.auth_user = None
            employee.password = ""
            context['user'] = employee
            return render(request, RENDER_CHANGE_PASSWORD_URL, context)
        else:
            return redirect(REDIRECT_HOME_URL)
    else:
        return redirect(REDIRECT_HOME_URL)

'''def changePassword(request):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        employee = getEmployeeToEdit(id, context['userData'].id, context['account'])
            employee.login = employee.auth_user.username
            employee.auth_user = None
            employee.password = ""
            context['user'] = employee
            return render(request, RENDER_USER_URL, context)
            else:
                return redirect(REDIRECT_USER_URL)
        else:
            return redirect(REDIRECT_USER_URL)
    else:
        return redirect(REDIRECT_HOME_URL)'''

def logoutUser(request):
    context = authUser(request)
    if context[USER_ACCOUNT] != USER_GUEST:
        logout(request)
        return redirect(REDIRECT_HOME_URL)
    else:
        return redirect(REDIRECT_HOME_URL)

def loginPage(request):
    context = authUser(request)
    if context[USER_ACCOUNT] == USER_GUEST:
        if request.method == 'POST':
            username = request.POST.get(LOGIN_USERNAME)
            password = request.POST.get(PASSWORD_USERNAME)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                employee = Employee.objects.filter(auth_user=user.id)
                if employee.exists():
                    if user.is_active:
                        login(request, user)
                        return redirect(REDIRECT_HOME_URL)
                    else:
                        messages.info(request, MESSAGES_LOGIN_ERROR)
                        return render(request, RENDER_LOGIN_URL, context)
                else:
                    login(request, user)
                    return redirect(REDIRECT_HOME_URL)
            else:
                messages.info(request, MESSAGES_LOGIN_ERROR)
                return render(request, RENDER_LOGIN_URL, context)
        else:
            return render(request, RENDER_LOGIN_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)

