from datetime import datetime
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect
from app.models import Employee, Unit, Employeetype, AuthUser
from app.view.auth.auth import authUser, UserData
from app.view.static.messagesTexts import MESSAGES_OPERATION_ERROR, MESSAGES_OPERATION_SUCCESS, MESSAGES_DATA_ERROR, \
    MESSAGES_DIFFPASSWORD_ERROR, MESSAGES_UNIT_ERROR, MESSAGES_ROLE_ERROR, MESSAGES_DUPLICATEUSER_ERROR, \
    MESSAGES_PASSWORD_ERROR
from app.view.static.urls import REDIRECT_HOME_URL, RENDER_USER_URL, REDIRECT_USERS_URL, REDIRECT_USER_URL, \
    RENDER_USERS_URL


def password_check(passwd):
    SpecialSym = ['$', '@', '#', '%']
    val = True

    if len(passwd) < 6:
        print('length should be at least 6')
        val = False

    if len(passwd) > 20:
        print('length should be not be greater than 8')
        val = False

    if not any(char.isdigit() for char in passwd):
        print('Password should have at least one numeral')
        val = False

    if not any(char.isupper() for char in passwd):
        print('Password should have at least one uppercase letter')
        val = False

    if not any(char.islower() for char in passwd):
        print('Password should have at least one lowercase letter')
        val = False

    if not any(char in SpecialSym for char in passwd):
        print('Password should have at least one of the symbols $@#')
        val = False
    if val:
        return val

def getEmployeeToEdit(id, userId, userRole):
    e = Employee.objects.filter(idemployee=int(id))
    if (len(e) > 0):
        e = e[0]
        if userRole == 'ADMIN' and e.idemployee != userId:
            return e
        elif userRole == 'PROCESS MANAGER' and (e.idemployeetype.name == 'MANAGER' or e.idemployeetype.name == 'USER'):
            return e
        elif userRole == 'MANAGER' and (e.idemployeetype.name == 'USER'):
            return e
        else:
            return None
    else:
        return None

def checkUserFromForm(request):
    name = request.POST.get('userName')
    surname = request.POST.get('userSurname')
    unit = request.POST.get('unitValue')
    employeeType = request.POST.get('roleValue')
    login = request.POST.get('userLogin')
    password = request.POST.get('userPassword')
    password2 = request.POST.get('userPassword2')
    #
    u = UserData()
    u.name = name
    u.surname = surname
    u.password = ''
    u.login = login
    u.unit = unit
    u.role = employeeType
    #
    if len(name) <= 2 or len(surname) <= 2 or len(login) <= 2 or len(password) < 4:
        return None, None, u, MESSAGES_DATA_ERROR
    if password != password2 or (len(password) == 0 and len(password2)):
        return None, None, u, MESSAGES_DIFFPASSWORD_ERROR
    if password_check(password) or (len(password) == 0 and len(password2)):
        return None, None, u, MESSAGES_PASSWORD_ERROR
    e = Employee()
    e.name = name
    e.surname = surname
    e.isactive = 1
    u = Unit.objects.filter(name=unit)
    if len(u) > 0:
        e.idunit = u[0]
    else:
        return None, None, u, MESSAGES_UNIT_ERROR
    et = Employeetype.objects.filter(name=employeeType)
    if len(et) > 0:
        e.idemployeetype = et[0]
        authUser = AuthUser()
        authUser.username = login
        authUser.email = login
        authUser.password = password
        authUser.is_superuser = False
        authUser.is_staff = False
        authUser.is_active = True
        authUser.date_joined = datetime.now()
    else:
        return None, None, u, MESSAGES_ROLE_ERROR
    return e, authUser, u, None
#
#   user delete function
#
def deleteUser(request, context, id):
    try:
        er = Employee.objects.filter(idemployee=int(id))
        if er.exists():
            au = User.objects.filter(username=er[0].auth_user.username)
            if au.exists():
                er[0].delete()
                au[0].delete()

            messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')
            return redirect(REDIRECT_USERS_URL)
        else:
            messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
            return redirect(REDIRECT_USERS_URL)
    except:
        messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
        return redirect(REDIRECT_USERS_URL)
#
#   user update function
#
def updateUser(request, context, id):
    e, authUser, u, MESSAGE = checkUserFromForm(request)
    if e is None:
        context['user'] = u
        messages.info(request, MESSAGE, extra_tags='error')
        return viewUser(request, context, id, u)
    try:
        er = Employee.objects.filter(idemployee=int(id))
        if er.exists():
            au = User.objects.filter(username=er[0].auth_user.username)
            if au.exists():
                au[0].set_password(authUser.password)
                au[0].username = authUser.username
                au[0].save()
                er[0].name = e.name
                er[0].surname = e.surname
                er[0].idunit = e.idunit
                er[0].idemployeetype = e.idemployeetype
                er[0].isactive = e.isactive
                er[0].save()
                messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')
                return redirect(REDIRECT_USERS_URL)
            else:
                context['user'] = u
                messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='error')
                return render(request, RENDER_USER_URL, context)
        else:
            context['user'] = u
            messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='error')
            return render(request, RENDER_USER_URL, context)
    except:
        context['user'] = u
        messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='error')
        return render(request, RENDER_USER_URL, context)
#
#   user save function
#
def saveUser(request, context, id =''):
    e, authUser, u, MESSAGE = checkUserFromForm(request)
    if e is None:
        context['user'] = u
        messages.info(request, MESSAGE, extra_tags='error')
        units = Unit.objects.all()
        context['units'] = units
        roles = Employeetype.objects.all()
        context['roles'] = roles
        return render(request, RENDER_USER_URL, context)
    try:
        au = AuthUser.objects.filter(username=authUser.username)
        if au.exists():
            messages.info(request, MESSAGES_DUPLICATEUSER_ERROR, extra_tags='error')
            return render(request, RENDER_USER_URL, context)
        user = User.objects.create_user(username=authUser.username,
                                        email=authUser.username,
                                        password=authUser.password)
        au = AuthUser.objects.filter(username=user.username)
        if au.exists():
            e.auth_user = au[0]
            e.save()
            messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')
            return redirect(REDIRECT_USERS_URL)
        else:
            messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
            return render(request, RENDER_USER_URL, context)
    except:
        context['user'] = u
        units = Unit.objects.all()
        context['units'] = units
        roles = Employeetype.objects.all()
        context['roles'] = roles
        messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
        return render(request, RENDER_USER_URL, context)
#
#   main operation user function
#
def viewUser(request, context, id = 0, u = 0):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        units = Unit.objects.all()
        context['units'] = units
        roles = Employeetype.objects.all()
        context['roles'] = roles
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
#
#   user change active
#
def userActive(request, id = ''):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        if len(id) > 0:
            employee = getEmployeeToEdit(id, context['userData'].id, context['account'])
            if employee is not None:
                if employee.isactive == 1:
                    employee.isactive = 0
                else:
                    employee.isactive = 1
                employee.save()
                return redirect(REDIRECT_USERS_URL)
            else:
                return redirect(REDIRECT_USERS_URL)
    else:
        return redirect(REDIRECT_HOME_URL)
#
#   main function
#
def userManager(request, id = '', operation = ''):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        if request.method == 'POST':
            #update
            if len(id) > 0 and operation == '':
                return updateUser(request, context, id)
            #delete
            elif len(id) > 0 and operation == 'delete':
                return deleteUser(request, context, id)
            else:
                # save - new unit
                return saveUser(request, context, id)
        else:
            #active
            if operation == 'active':
                return userActive(request, id)
            #view
            else:
                return viewUser(request, context, id)
    else:
        return redirect(REDIRECT_HOME_URL)
#
#   view users
#
def usersView(request):
    context = authUser(request)
    if context['account'] != 'GUEST':
        if (context['account'] == 'ADMIN'):
            employeesData = Employee.objects.filter(~Q(auth_user=context['userData'].id))
        elif (context['account'] == 'PROCESS MANAGER'):
            employeesData = Employee.objects.filter(Q(idemployeetype__name='USER') | Q(idemployeetype__name='MANAGER'))
        elif (context['account'] == 'MANAGER'):
            employeesData = Employee.objects.filter(idemployeetype__name='USER')
        context['employeesData'] = employeesData
        return render(request, RENDER_USERS_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)