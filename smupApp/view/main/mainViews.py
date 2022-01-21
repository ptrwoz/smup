from django.shortcuts import render
from smupApp.view.auth.auth import authUser
from smupApp.view.static.urls import RENDER_HOME_URL

#
#   home page
#
def home(request):
    context = authUser(request)
    return render(request, RENDER_HOME_URL, context)
