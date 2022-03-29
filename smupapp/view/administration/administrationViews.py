#
#   main function
#
from django.shortcuts import redirect, render

from smupapp.view.auth.auth import authUser
from smupapp.view.static.urls import REDIRECT_HOME_URL, RENDER_ADMINSTRATION_URL


def administrationView(request):
    context = authUser(request)
    if context['account'] == 'ADMIN':

        return render(request, RENDER_ADMINSTRATION_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)

def administrationManager(request):
    context = authUser(request)
    if context['account'] != 'GUEST':
        if request.method == 'POST':
            print()
        else:
            print()
    else:
        return redirect(REDIRECT_HOME_URL)