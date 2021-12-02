from django.shortcuts import render
from app.view.auth.auth import authUser
from app.view.static.urls import RENDER_HOME_URL

#
#   home page
#
def home(request):
    context = authUser(request)
    return render(request, RENDER_HOME_URL, context)
