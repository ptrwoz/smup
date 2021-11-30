from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app.models import Employee
from app.models import Process
from app.view.auth.auth import authUser


def processView(request):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER':
        if request.method == 'POST':
            name = request.POST.get('name')
            print()
        else:
            #userData = context['userData']
            processData = Process.objects.all()
            context['processData'] = processData
            return render(request, 'process/process.html', context)
    else:
        return redirect('home')
