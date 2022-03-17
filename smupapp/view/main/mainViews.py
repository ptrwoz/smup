from django.shortcuts import render
from smupapp.view.auth.auth import authUser
from smupapp.view.static.urls import RENDER_HOME_URL
from django.template import RequestContext
#
#   home page
#
def home(request):
    context = authUser(request)
    return render(request, RENDER_HOME_URL, context)
