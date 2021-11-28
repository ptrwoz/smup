from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from app.view.auth.auth import authUser

def profilUser(request):
    context = authUser(request)
    if context['account'] != 'GUEST':
        return render(request, 'auth/profil.html', context)
    else:
        return redirect('home')

def logoutUser(request):
    context = authUser(request)
    if context['account'] != 'GUEST':
        logout(request)
        return redirect('home')
    else:
        return redirect('home')

def loginPage(request):
    context = authUser(request)
    if context['account'] == 'GUEST':
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Błędne logowanie!')
                return render(request, "auth/login.html", context)
        else:
            return render(request, "auth/login.html", context)
    else:
        return redirect('home')

