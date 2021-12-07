from datetime import datetime

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect
from app.models import Employee, Unit, Employeetype, AuthUser
from app.view.auth.auth import authUser, UserData
from app.view.static.messagesTexts import MESSAGES_OPERATION_ERROR, MESSAGES_OPERATION_SUCCESS
from app.view.static.urls import REDIRECT_HOME_URL, RENDER_USER_URL, REDIRECT_USERS_URL


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
    if len(name) <= 2 and len(surname) <= 2 and len(login) <= 2 and len(password) < 4:
        return None, None, u
    if password != password2:
        return None, None, u
    e = Employee()
    e.name = name
    e.surname = surname
    u = Unit.objects.filter(name=unit)
    if len(u) > 0:
        e.idunit = u[0]
    else:
        messages.info(request, 'Błędna jednostka')
        return None, None, u
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
        return None, None, u
    return e, authUser, u

#def deleteUser(request, context, id):


def updateUser(request, context, id):

    '''else:
        messages.info(request, 'Błędny typ konta')
        return viewUser(request, context, id)'''
# request was empty
#
#   user save function
#
def saveUser(request, context, id):
    e, authUser, u = checkUserFromForm(request)
    if e is None:
        context['user'] = u
        messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
        return viewUser(request, context, id, u)
    try:
        authUser.save()
        e.auth_user = authUser
        e.save()
        messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')
        return render(request, RENDER_USER_URL, context)
    except:
        authUser.delete()
        e.delete()
        context['user'] = u
        messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='error')
        return render(request, RENDER_USER_URL, context)
#
#   main operation user function
#
def viewUser(request, context, id = '', u = ''):
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        units = Unit.objects.all()
        context['units'] = units
        roles = Employeetype.objects.all()
        context['roles'] = roles
        if id == '':
            if u == '':
                context['user'] = UserData()
            else:
                context['user'] = u
            return render(request, RENDER_USER_URL, context)
        elif len(id) > 0 and id.isnumeric():
            e = getEmployeeToEdit(id, context['userData'].id, context['account'])
            if e is not None:
                e.login = e.auth_user.username
                e.auth_user = None
                e.password = ""
                context['user'] = e
                return render(request, RENDER_USER_URL, context)
            else:
                return redirect(REDIRECT_USERS_URL)
        else:
            return redirect(REDIRECT_USERS_URL)
    else:
        return redirect(REDIRECT_HOME_URL)

def userView(request, id = '', delete = ''):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        #save and update
        if request.method == 'POST':
            if len(id) > 0 and delete == '':
                return updateUser(request, context, id)
            elif len(id) > 0 and delete == 'delete':
                return saveUser(request, context, id)
            elif delete == 'delete':
                return redirect(REDIRECT_HOME_URL)
            else:
                return saveUser(request, context, id)
        else:
            return viewUser(request, context, id)
    else:
        return redirect(REDIRECT_HOME_URL)
#
#   main view users function
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
        return render(request, 'user/users.html', context)
    else:
        return redirect(REDIRECT_HOME_URL)