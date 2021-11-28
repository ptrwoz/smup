from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from app.view.auth.auth import authUser


def importExportPage(request):
    context = authUser(request)
    if context['account'] == 'GUEST':
        return redirect('home')
    else:
        return render(request, "data/importExport.html", context)
