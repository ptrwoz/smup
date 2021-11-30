from datetime import datetime

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect
from app.models import Employee, Unit, Employeetype, AuthUser
from app.view.auth.auth import authUser, UserData

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

#
#
#
def viewUser(request, context, id):
    units = Unit.objects.all()
    context['units'] = units
    roles = Employeetype.objects.all()
    context['roles'] = roles
    if id == 0:
        context['user'] = UserData()
        return render(request, 'user/user.html', context)
    elif len(id) == 0:
        context['user'] = UserData()
        return render(request, 'user/user.html', context)
    elif len(id) > 0 and id.isnumeric():
        e = getEmployeeToEdit(id, context['userData'].id, context['account'])
        if e is not None:
            e.login = e.auth_user.username
            e.auth_user = None
            e.password = ""
            context['user'] = e
            return render(request, 'user/user.html', context)
        else:
            return redirect('users')
    else:
        return redirect('users')

'''def createAuthUser(username, password):
    if username and password:
        u, created = User.objects.get_or_create(userName, userMail)
        if created:
        else:
    # user was retrieved
    else:'''

# request was empty
#
#   user save function
#
def saveUser(request, context, id):
    name = request.POST.get('userName')
    surname = request.POST.get('userSurname')
    unit = request.POST.get('unitValue')
    employeeType = request.POST.get('roleValue')
    login = request.POST.get('userLogin')
    password = request.POST.get('userPassword')
    password2 = request.POST.get('userPassword2')
    if (password != password2):
        messages.info(request, 'Hasła sa różne')
        return viewUser(request, context, id)
    e = Employee()
    e.name = name
    e.surname = surname
    u = Unit.objects.filter(name = unit)
    if len(u) > 0:
        e.idunit = u[0]
    else:
        messages.info(request, 'Błędna jednostka')
        return viewUser(request, context, id)
    et = Employeetype.objects.filter(name = employeeType)
    if len(et) > 0:
        e.idemployeetype = et[0]
    else:
        messages.info(request, 'Błędny typ konta')
        return viewUser(request, context, id)
    authUser = AuthUser()
    authUser.username = login
    authUser.email = login
    authUser.password = password
    authUser.is_superuser = False
    authUser.is_staff = False
    authUser.is_active = True
    authUser.date_joined = datetime.now()
    authUser.save()
    # au = AuthUser()
    #try:
    authUser.save()
    e.auth_user = authUser
    e.save()
    messages.info(request, 'Zapisano')
    return render(request, 'user/user.html', context)
    #except:
        #messages.info(request, 'Błąd zapisu')
        #return viewUser(request, context, id)
#
#   main operation user function
#
def userView(request, id = 0):
    context = authUser(request)
    if context['account'] != 'GUEST':
        #save and update
        if request.method == 'POST':
            return saveUser(request, context, id)
        elif request.method == 'DELETE':
            return redirect('home')
        #view user
        else:
            return viewUser(request, context, id)
    else:
        return redirect('home')
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
        return redirect('home')