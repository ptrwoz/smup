from smupApp.models import Employee
from smupApp.view.static.dataModels import UserData
from smupApp.view.static.staticValues import USER_LABEL, USER_ACCOUNT, USER_DATA, USER_GUEST


#
# auth user function
#
def authUser(request):
    context = dict()
    userData = UserData()
    if request.user.is_authenticated and request.user.is_active:
        userName = request.user
        employees = Employee.objects.filter(auth_user=userName.id)
        if employees.exists():
            employee = employees[0]
            userData.id = employee.id_employee
            userData.name = str(employee.name)
            userData.surname = str(employee.surname)
            userData.unit = str(employee.id_unit.name)
            userData.role = str(employee.id_employeetype.name)
            userData.login = str(employee.auth_user.username)
            context[USER_LABEL] = employee.name + " " + employee.surname
            context[USER_ACCOUNT] = str(employee.id_employeetype.name)
            context[USER_DATA] = userData
        else:
            context[USER_LABEL] = userName
            if userName.username == 'admin':
                userData.id = 0
                userData.name = 'ADMIN'
                userData.surname = 'ADMIN'
                userData.unit = 'ADMIN'
                userData.role = 'ADMIN'
                userData.login = 'ADMIN'
                context[USER_LABEL] = 'ADMIN'
                context[USER_ACCOUNT] = 'ADMIN'
                context[USER_DATA] = userData
                context[USER_ACCOUNT] = str('ADMIN')
            else:
                context[USER_ACCOUNT] = USER_GUEST
    else:
        context[USER_ACCOUNT] = USER_GUEST
    return context
