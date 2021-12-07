from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from app.view.auth.auth import authUser
from app.view.static.urls import RENDER_PROFIL_URL, REDIRECT_HOME_URL, RENDER_LOGIN_URL

def profilUser(request):
    context = authUser(request)
    if context['account'] != 'GUEST':
        return render(request, RENDER_PROFIL_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)

def logoutUser(request):
    context = authUser(request)
    if context['account'] != 'GUEST':
        logout(request)
        return redirect(REDIRECT_HOME_URL)
    else:
        return redirect(REDIRECT_HOME_URL)

def loginPage(request):
    context = authUser(request)
    if context['account'] == 'GUEST':
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(REDIRECT_HOME_URL)
            else:
                messages.info(request, 'Błędne logowanie!')
                return render(request, RENDER_LOGIN_URL, context)
        else:
            return render(request, RENDER_LOGIN_URL, context)
    else:
        return redirect('home')

