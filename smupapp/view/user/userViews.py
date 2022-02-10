from datetime import datetime
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render, redirect
from smupapp.models import Employee, Unit, Employeetype, AuthUser, Rule, RuleHasEmployee
from smupapp.view.auth.auth import authUser, UserData
from smupapp.view.static.messagesTexts import MESSAGES_OPERATION_ERROR, MESSAGES_OPERATION_SUCCESS, \
    MESSAGES_DIFFPASSWORD_ERROR, MESSAGES_UNIT_ERROR, MESSAGES_ROLE_ERROR, MESSAGES_DUPLICATEUSER_ERROR, \
    MESSAGES_PASSWORD_ERROR, MESSAGES_DATA_NAMESURNAME_ERROR, MESSAGES_DATA_LOGINLEN_ERROR, \
    MESSAGES_DATA_LOGINEXIST_ERROR, MESSAGES_OPERATION_USER_DELETE_ERROR, MESSAGES_OPERATION_USER_HAS_RULE_SUCCESS
from smupapp.view.static.staticValues import USER_ACCOUNT, PAGEINATION_SIZE, USER_ADMIN, USER_PROCESS_MANAGER, USER_USER, USER_MANAGER, \
    USER_GUEST
from smupapp.view.static.urls import REDIRECT_HOME_URL, RENDER_USER_URL, REDIRECT_USERS_URL, REDIRECT_USER_URL, \
    RENDER_USERS_URL
from smupapp.view.unit.unitViews import getUnitsToEdit

#
#   check password by conditions
#
def passwordCheck(passwd):
    SpecialSym = ['$', '@', '#', '%', '!', '*']
    result = True

    if len(passwd) < 6:
        print('length should be at least 6')
        result = False

    elif len(passwd) > 20:
        print('length should be not be greater than 8')
        result = False

    elif not any(char.isdigit() for char in passwd):
        print('Password should have at least one numeral')
        result = False

    elif not any(char.isupper() for char in passwd):
        print('Password should have at least one uppercase letter')
        result = False
    
    elif not any(char in SpecialSym for char in passwd):
        print('Password should have at least one of the symbols $@#')
        result = False
    return result
#
#   get user roles by curretn user role
#
def getRolesToEdit(userRole):
    if userRole == USER_ADMIN:
        roles = Employeetype.objects.filter(Q(name = USER_PROCESS_MANAGER) | Q(name = USER_MANAGER) | Q(name = USER_USER)).order_by('name')
    elif userRole == USER_PROCESS_MANAGER:
        roles = Employeetype.objects.filter(Q(name = USER_MANAGER) | Q(name = USER_USER)).order_by('name')
    elif userRole == USER_MANAGER:
        roles = Employeetype.objects.filter(Q(name = USER_USER)).order_by('name')
    else:
        roles = None
    return roles
#
#   get all employyes
#
def getEmployeeToEdit(id, userId, userRole):
    employees = Employee.objects.filter(id_employee=int(id))
    if employees.exists():
        employee = employees[0]
        if userRole == USER_ADMIN and employee.id_employee != userId:
            return employee
        elif userRole == USER_PROCESS_MANAGER and (employee.id_employeetype.name == USER_MANAGER or \
                                                   employee.id_employeetype.name == USER_USER):
            return employee
        elif userRole == USER_MANAGER and (employee.id_employeetype.name == USER_USER):
            return employee
    return None
#
#   check data from form
#
def checkUserFromForm(request, isUpdated):
    messages = []
    name = request.POST.get('userName')
    surname = request.POST.get('userSurname')
    unit = request.POST.get('unitValue')
    employeeType = request.POST.get('roleValue')
    login = request.POST.get('userLogin')
    password = request.POST.get('userPassword')
    password2 = request.POST.get('userPassword2')
    #
    formUser = Employee()
    formUser.name = name
    formUser.surname = surname
    formUser.password = ''
    formUser.login = login
    formUser.id_unit = Unit()
    formUser.id_unit.name = unit
    formUser.id_employeetype = Employeetype()
    formUser.id_employeetype.name = employeeType
    #
    if password != password2:
        messages.append(MESSAGES_DIFFPASSWORD_ERROR)
    if len(formUser.name) <= 2 or len(formUser.surname) <= 2:
        messages.append(MESSAGES_DATA_NAMESURNAME_ERROR)
    if AuthUser.objects.filter(username=formUser.login).exists() and not isUpdated:
        messages.append(MESSAGES_DATA_LOGINEXIST_ERROR)
    if len(formUser.login) < 6:
        messages.append(MESSAGES_DATA_LOGINLEN_ERROR)
    if ((len(password) == 0 and len(password2) == 0) and not isUpdated) or \
            (not passwordCheck(password) and not isUpdated):
        messages.append(MESSAGES_PASSWORD_ERROR)
    if len(messages) > 0:
        return None, None, formUser, messages
    # create employee
    employee = Employee()
    employee.name = formUser.name
    employee.surname = formUser.surname
    units = Unit.objects.filter(name=formUser.id_unit.name)
    if units.exists():
        employee.id_unit = units[0]
    else:
        messages.append(MESSAGES_UNIT_ERROR)
        return None, None, formUser, messages

    employeeTypes = Employeetype.objects.filter(name=formUser.id_employeetype.name)
    if employeeTypes.exists():
        employee.id_employeetype = employeeTypes[0]
        # create auth user
        authUser = AuthUser()
        authUser.username = formUser.login
        authUser.email = formUser.login
        authUser.password = password
        authUser.is_superuser = 0
        authUser.is_staff = 0
        authUser.is_active = 1
        authUser.date_joined = datetime.now()
    else:
        messages.append(MESSAGES_UNIT_ERROR)
        return None, None, formUser, messages

    return employee, authUser, formUser, messages

#
#   user delete function
#
def deleteUser(request, context, id):
    if True:
    #try:
        id = int(id)
        employee = Employee.objects.filter(id_employee=id)
        if employee.exists():
            authUser = User.objects.filter(username=employee[0].auth_user.username)
            if authUser.exists():
                employees = RuleHasEmployee.objects.filter(employee_id_employee=id)
                if employees.exists():
                    messages.info(request, MESSAGES_OPERATION_USER_HAS_RULE_SUCCESS, extra_tags='error')
                    return redirect(REDIRECT_USERS_URL)
                else:
                    employee[0].delete()
                    authUser[0].delete()
            messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')
            return redirect(REDIRECT_USERS_URL)
        else:
            messages.info(request, MESSAGES_OPERATION_USER_DELETE_ERROR, extra_tags='error')
            return redirect(REDIRECT_USERS_URL)
    #except:
        messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
        return redirect(REDIRECT_USERS_URL)
#
#   user update function
#
def updateUser(request, context, id):
    employee, newAuthUser, formUser, messageTexts = checkUserFromForm(request, True)
    if employee is None:
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
        return render(request, RENDER_USER_URL, context)
#
#   user save function
#
def saveUser(request, context):
    e, authUser, u, messageTexts = checkUserFromForm(request, False)
    if e is None:
        context['user'] = u
        for messageText in messageTexts:
            messages.info(request, messageText, extra_tags='error')
        #messages.info(request, MESSAGE, extra_tags='error')
        units = getUnitsToEdit(context[USER_ACCOUNT])
        context['units'] = units
        roles = Employeetype.objects.all()
        context['roles'] = roles
        return render(request, RENDER_USER_URL, context)
    #if True:
    try:
        au = AuthUser.objects.filter(username=authUser.username)
        if au.exists():
            context['user'] = u
            units = getUnitsToEdit(context[USER_ACCOUNT])
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
def viewUser(request, id = 0, u = 0):
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
                return saveUser(request, context)
        else:
            #active
            if operation == 'active':
                page = request.GET.get('page')
                return userActive(request, id, page)
            #view
            else:
                return viewUser(request, id)
    else:
        return redirect(REDIRECT_HOME_URL)

#
#   reduce users password
#
def employeesPasswordReduce(employeesData):
    for e in employeesData:
        e.auth_user.password = ''
    return employeesData
#
#   get employeesByRole
#
def getEmployeesByRole(user):
    if (user.role == 'ADMIN'):
        employeesData = Employee.objects.filter(~Q(id_employee=user.id)).order_by('surname', 'name')
    elif (user.role == 'PROCESS MANAGER'):
        employeesData = Employee.objects.filter(
            ~Q(id_employee=user.id) & Q(id_employeetype__name='USER') | Q(
                id_employeetype__name='MANAGER')).order_by('surname', 'name')
    elif (user.role == 'MANAGER'):
        employeesData = Employee.objects.filter(
            ~Q(id_employee=user.id) & Q(id_employeetype__name='USER')).order_by('surname', 'name')
    employeesData = employeesPasswordReduce(employeesData)
    return employeesData

#
#   view users
#
def usersView(request):
    context = authUser(request)
    if context['account'] != USER_GUEST:
        employeesData = getEmployeesByRole(context['userData'])
        page = request.GET.get('page', 1)
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