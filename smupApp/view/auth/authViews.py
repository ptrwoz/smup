from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from smupApp.models import Employee
from smupApp.view.auth.auth import authUser
from smupApp.view.static.messagesTexts import MESSAGES_LOGIN_ERROR
from smupApp.view.static.staticValues import USER_GUEST, USER_ACCOUNT, LOGIN_USERNAME, PASSWORD_USERNAME
from smupApp.view.static.urls import RENDER_PROFIL_URL, REDIRECT_HOME_URL, RENDER_LOGIN_URL

def profilUser(request):
    context = authUser(request)
    if context[USER_ACCOUNT] != USER_GUEST:
        return render(request, RENDER_PROFIL_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)

def logoutUser(request):
    context = authUser(request)
    if context[USER_ACCOUNT] != USER_GUEST:
        logout(request)
        return redirect(REDIRECT_HOME_URL)
    else:
        return redirect(REDIRECT_HOME_URL)

def loginPage(request):
    context = authUser(request)
    if context[USER_ACCOUNT] == USER_GUEST:
        if request.method == 'POST':
            username = request.POST.get(LOGIN_USERNAME)
            password = request.POST.get(PASSWORD_USERNAME)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                employee = Employee.objects.filter(auth_user=user.id)
                if employee.exists():
                    if user.is_active:
                        login(request, user)
                        return redirect(REDIRECT_HOME_URL)
                    else:
                        messages.info(request, MESSAGES_LOGIN_ERROR)
                        return render(request, RENDER_LOGIN_URL, context)
                else:
                    login(request, user)
                    return redirect(REDIRECT_HOME_URL)
            else:
                messages.info(request, MESSAGES_LOGIN_ERROR)
                return render(request, RENDER_LOGIN_URL, context)
        else:
            return render(request, RENDER_LOGIN_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)

