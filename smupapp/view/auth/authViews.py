from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from smupapp.models import Employee, AuthUser
from smupapp.view.auth.auth import authUser
from smupapp.view.static.dataModels import UserData
from smupapp.view.static.messagesTexts import MESSAGES_LOGIN_ERROR, MESSAGES_OPERATION_SUCCESS, \
    MESSAGES_OPERATION_ERROR, MESSAGES_DIFFPASSWORD_ERROR, MESSAGES_DATA_NAMESURNAME_ERROR, \
    MESSAGES_DATA_LOGINLEN_ERROR, MESSAGES_ADMIN_ACCOUNT, MESSAGES_PASSWORD_ERROR
from smupapp.view.static.staticValues import USER_GUEST, USER_ACCOUNT, LOGIN_USERNAME, PASSWORD_USERNAME
from smupapp.view.static.urls import RENDER_PROFIL_URL, REDIRECT_HOME_URL, RENDER_LOGIN_URL, RENDER_CHANGE_PASSWORD_URL, \
    RENDER_USER_URL, REDIRECT_USER_URL
from smupapp.view.unit.unitViews import getUnitsToEdit
from smupapp.view.user.userViews import getEmployeeToEdit, getRolesToEdit, passwordCheck


def profilUserView(request):
    context = authUser(request)
    if context[USER_ACCOUNT] != USER_GUEST:
        return render(request, RENDER_PROFIL_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)

def changePassword(request):
    context = authUser(request)
    '''if employee is None:
        context['user'] = formUser
        for messageText in messageTexts:
            messages.info(request, messageText, extra_tags='error')
        return viewUser(request, id, formUser)
    try:
        otherEmployees = Employee.objects.filter(id_employee=int(id))
        if otherEmployees.exists():
            otherEmployee = otherEmployees[0]
            authUsers = User.objects.filter(username=otherEmployee.auth_user.username)
            if authUsers.exists():
                authUser = authUsers[0]
                if len(newAuthUser.password) > 0:
                    authUser.set_password(newAuthUser.password)
                authUser.username = newAuthUser.username
                authUser.save()
                otherEmployee.name = employee.name
                otherEmployee.surname = employee.surname
                otherEmployee.id_unit = employee.id_unit
                otherEmployee.id_employeetype = employee.id_employeetype
                otherEmployee.save()
                messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')
                return redirect(REDIRECT_USERS_URL)
            else:
                context['user'] = formUser
                messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='error')
                return render(request, RENDER_USER_URL, context)
        else:
            context['user'] = formUser
            messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='error')
            return render(request, RENDER_USER_URL, context)
    except:
        context['user'] = formUser
        messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='error')
        return render(request, RENDER_USER_URL, context)'''

def changePasswordView(request):
    context = authUser(request)
    formUser = Employee()
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER' or context['account'] == 'USER':
        employees = Employee.objects.filter(id_employee=int(context['userData'].id))
        if employees.exists():
            if len(request.POST):
                formUser = Employee()
                formUser.password = ''
                context['user'] = formUser
                password = request.POST.get('userPassword')
                password2 = request.POST.get('userPassword2')
                if password != password2:
                    messages.info(request, MESSAGES_DIFFPASSWORD_ERROR, extra_tags='error')
                    return render(request, RENDER_CHANGE_PASSWORD_URL, context)
                if not passwordCheck(password):
                    messages.info(request, MESSAGES_PASSWORD_ERROR, extra_tags='error')
                    return render(request, RENDER_CHANGE_PASSWORD_URL, context)
                employee = employees[0]
                authUsers = User.objects.filter(username=employee.auth_user.username)
                if authUsers.exists():
                    authUserData = authUsers[0]
                    if len(password) > 0:
                        authUserData.set_password(password)
                    authUserData.save()
                    messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')
                else:
                    messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
            #elif request.GET:
        else:
            messages.info(request, MESSAGES_ADMIN_ACCOUNT, extra_tags='error')
        return render(request, RENDER_CHANGE_PASSWORD_URL, context)
        #else:
        #    return redirect(REDIRECT_HOME_URL)
    else:
        return redirect(REDIRECT_HOME_URL)

#
#   main operation user function
#
def userPasswordView(request, id = 0, u = 0):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        units = getUnitsToEdit(context[USER_ACCOUNT])
        context['units'] = units
        context['roles'] = getRolesToEdit(context[USER_ACCOUNT])
        if id == '':
            if u == 0:
                context['user'] = UserData()
            else:
                context['user'] = u
            return render(request, RENDER_USER_URL, context)
        elif id.isnumeric():
            employee = getEmployeeToEdit(id, context['userData'].id, context['account'])
            if employee is not None:
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
        return redirect(REDIRECT_HOME_URL)

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

