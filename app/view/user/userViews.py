from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect
from app.models import Employee, Unit, Employeetype
from app.view.auth.auth import authUser, UserData


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

#
#   user save function
#
def saveUser(request, context, id):
    name = request.POST.get('userName')
    surname = request.POST.get('userSurname')
    unit = request.POST.get('unitValue')
    employeeType = request.POST.get('roleValue')
    e = Employee()
    e.name = name
    e.surname = surname
    u = Unit()
    u.name = unit
    e.idunit = u
    et = Employeetype()
    et.name = employeeType
    e.idemployeetype = et
    # au = AuthUser()
    try:
        e.save()
        messages.info(request, 'Zapisano')
        return render(request, 'user/user.html', context)
    except:
        messages.info(request, 'Błąd zapisu')
        return viewUser(request, context, id)
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