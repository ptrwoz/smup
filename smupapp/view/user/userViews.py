from datetime import datetime
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render, redirect
from smupapp.models import Employee, Unit, Employeetype, AuthUser
from smupapp.view.auth.auth import authUser, UserData
from smupapp.view.static.messagesTexts import MESSAGES_OPERATION_ERROR, MESSAGES_OPERATION_SUCCESS, MESSAGES_DATA_ERROR, \
    MESSAGES_DIFFPASSWORD_ERROR, MESSAGES_UNIT_ERROR, MESSAGES_ROLE_ERROR, MESSAGES_DUPLICATEUSER_ERROR, \
    MESSAGES_PASSWORD_ERROR
from smupapp.view.static.staticValues import USER_ACCOUNT, PAGEINATION_SIZE
from smupapp.view.static.urls import REDIRECT_HOME_URL, RENDER_USER_URL, REDIRECT_USERS_URL, REDIRECT_USER_URL, \
    RENDER_USERS_URL

def password_check(passwd):
    SpecialSym = ['$', '@', '#', '%', '!', '*']
    val = True

    if len(passwd) < 6:
        print('length should be at least 6')
        val = False

    elif len(passwd) > 20:
        print('length should be not be greater than 8')
        val = False

    elif not any(char.isdigit() for char in passwd):
        print('Password should have at least one numeral')
        val = False

    elif not any(char.isupper() for char in passwd):
        print('Password should have at least one uppercase letter')
        val = False

    elif not any(char.islower() for char in passwd):
        print('Password should have at least one lowercase letter')
        val = False

    elif not any(char in SpecialSym for char in passwd):
        print('Password should have at least one of the symbols $@#')
        val = False
    return val

def getRoleToEdit(userRole):
    if userRole == 'ADMIN':
        roles = Employeetype.objects.all().order_by('name')
    elif userRole == 'PROCESS MANAGER':
        roles = Employeetype.objects.filter(Q(name = 'MANAGER') | Q(name = 'USER')).order_by('name')
    elif userRole == 'MANAGER':
        roles = Employeetype.objects.filter(Q(name = 'USER')).order_by('name')
    else:
        roles = None
    return roles

def getEmployeeToEdit(id, userId, userRole):
    e = Employee.objects.filter(id_employee=int(id))
    if (len(e) > 0):
        e = e[0]
        if userRole == 'ADMIN' and e.id_employee != userId:
            return e
        elif userRole == 'PROCESS MANAGER' and (e.id_employeetype.name == 'MANAGER' or e.id_employeetype.name == 'USER'):
            return e
        elif userRole == 'MANAGER' and (e.id_employeetype.name == 'USER'):
            return e
        else:
            return None
    else:
        return None

def checkUserFromForm(request, isUpdated):
    name = request.POST.get('userName')
    surname = request.POST.get('userSurname')
    unit = request.POST.get('unitValue')
    employeeType = request.POST.get('roleValue')
    login = request.POST.get('userLogin')
    password = request.POST.get('userPassword')
    password2 = request.POST.get('userPassword2')
    #
    u = Employee()
    u.name = name
    u.surname = surname
    u.password = ''
    u.login = login
    u.id_unit = Unit()
    u.id_unit.name = unit
    u.id_employeetype = Employeetype()
    u.id_employeetype.name = employeeType
    #
    if len(name) <= 2 or len(surname) <= 2 or len(login) <= 2:
        return None, None, u, MESSAGES_DATA_ERROR
    if password != password2:
        return None, None, u, MESSAGES_DIFFPASSWORD_ERROR
    if (len(password) == 0 and len(password2) == 0) and not isUpdated:
        return None, None, u, MESSAGES_PASSWORD_ERROR
    if not password_check(password) and not isUpdated:
        return None, None, u, MESSAGES_PASSWORD_ERROR
    e = Employee()
    e.name = name
    e.surname = surname
    #e.isactive = 1
    units = Unit.objects.filter(name=unit)
    if units.exists():
        e.id_unit = units[0]
    else:
        return None, None, u, MESSAGES_UNIT_ERROR
    et = Employeetype.objects.filter(name=employeeType)
    if et.exists():
        e.id_employeetype = et[0]
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
        er = Employee.objects.filter(id_employee=int(id))
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
    e, authUser, u, MESSAGE = checkUserFromForm(request, True)
    if e is None:
        context['user'] = u
        messages.info(request, MESSAGE, extra_tags='error')
        return viewUser(request, context, id, u)
    try:
        er = Employee.objects.filter(id_employee=int(id))
        if er.exists():
            au = User.objects.filter(username=er[0].auth_user.username)
            if au.exists():
                aut = au[0]
                if len(authUser.password) > 0:
                    aut.set_password(authUser.password)
                aut.username = authUser.username
                aut.save()
                emp = er[0]
                emp.name = e.name
                emp.surname = e.surname
                emp.id_unit = e.id_unit
                emp.id_employeetype = e.id_employeetype
                #emp.isactive = e.isactive
                emp.save()

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
    e, authUser, u, MESSAGE = checkUserFromForm(request, False)
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
            context['user'] = u
            units = Unit.objects.all()
            context['units'] = units
            roles = Employeetype.objects.all()
            context['roles'] = roles
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
        units = Unit.objects.all().order_by('name')
        context['units'] = units

        context['roles'] =  getRoleToEdit(context[USER_ACCOUNT])
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
def userActive(request, id = '', page = ''):
    context  = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        if len(id) > 0:
            employee = getEmployeeToEdit(id, context['userData'].id, context['account'])
            if employee is not None :
                auth = employee.auth_user
                if auth.is_active == 1:
                    auth.is_active = 0
                else:
                    auth.is_active = 1
                auth.save()
                if page != '':
                    return redirect('../../'+ REDIRECT_USERS_URL + '?page=' + page)
                else:
                    return redirect(REDIRECT_USERS_URL)
            else:
                return redirect(REDIRECT_USERS_URL)
    else:
        return redirect(REDIRECT_HOME_URL)
#
#   main function
#
def userManager(request, id = '', operation = '', page=''):
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
                page = request.GET.get('page')
                return userActive(request, id, page)
            #view
            else:
                return viewUser(request, context, id)
    else:
        return redirect(REDIRECT_HOME_URL)
#
#   reduce susers password
#
def employeesDataReduce(employeesData):
    for e in employeesData:
        e.auth_user.password = ''
    return employeesData
#
#   view users
#
def usersView(request):
    context = authUser(request)
    if context['account'] != 'GUEST':
        if (context['account'] == 'ADMIN'):
            employeesData = Employee.objects.filter(~Q(id_employee=context['userData'].id)).order_by('surname', 'name')
        elif (context['account'] == 'PROCESS MANAGER'):
            employeesData = Employee.objects.filter(~Q(id_employee=context['userData'].id) & Q(id_employeetype__name='USER') | Q(id_employeetype__name='MANAGER')).order_by('surname', 'name')
        elif (context['account'] == 'MANAGER'):
            employeesData = Employee.objects.filter(~Q(id_employee=context['userData'].id) & Q(id_employeetype__name='USER')).order_by('surname', 'name')
        page = request.GET.get('page', 1)
        employeesData = employeesDataReduce(employeesData)
        paginator = Paginator(employeesData, PAGEINATION_SIZE)
        try:
            employeesData = paginator.page(page)
        except PageNotAnInteger:
            employeesData = paginator.page(1)
        except EmptyPage:
            employeesData = paginator.page(paginator.num_pages)
        context['employeesData'] = employeesData
        return render(request, RENDER_USERS_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)