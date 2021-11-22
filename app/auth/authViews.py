from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app.models import Employee

class UserData:
    name = ""
    surname = ""
    pass


def profilUser(request):
    context = dict()
    userData = UserData()
    if request.user.is_authenticated:
        userName = request.user
        employee = Employee.objects.filter(auth_user=userName.id)
        if employee.exists():
            context['userLabel'] = employee[0].name + " " + employee[0].surname
            context['account'] = str(employee[0].idemployeetype.name)
            userData.name = str(employee[0].name)
            userData.surname = str(employee[0].surname)
            context['userData'] = userData
        else:
            context['userLabel'] = userName
            context['account'] = 'GUEST'
    else:
        context['account'] = 'GUEST'
    return render(request, 'auth/profil.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Błędne logowanie!')

        context = {}
        return render(request, "auth/login.html", context)