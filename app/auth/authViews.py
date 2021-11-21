from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app.models import Employee

def profilUser(request):
    context = dict()
    if request.user.is_authenticated:
        context['logged'] = 'yes'
        userData = request.user
        employee = Employee.objects.filter(auth_user=userData.id)
        if (employee.exists()):
            userData.email = userData.email
            userData.label = employee[0].name + " " + employee[0].surname
            userData.idemployeeType = employee[0].idemployeetype.name
            userData.unit = employee[0].idunit.name
        else:
            userData.label = userData
        context['userData'] = userData
        return render(request, 'auth/profil.html', context)
    else:
        context['logged'] = 'no'
        return redirect('home')

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
                messages.info(request, 'Login process error!')

        context = {}
        return render(request, "auth/login.html", context)