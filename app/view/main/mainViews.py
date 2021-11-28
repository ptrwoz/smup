from django.shortcuts import render
from app.view.auth.auth import authUser


def home(request):
    context = authUser(request)
    return render(request, 'main/home.html', context)
