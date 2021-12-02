from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app.models import Employee
from app.models import Process
from app.view.auth.auth import authUser

def initChapterNo(processData):
    for p in processData:
        sp = p
        no = '.' + str(sp.idsubprocess)
        sp = sp.idmainprocess
        while sp is not None:
            no = no + '.' + str(sp.idsubprocess)
            sp = sp.idmainprocess_id
        p.no = no[::-1]
    return processData
def processView(request):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER':
        if request.method == 'POST':
            name = request.POST.get('name')
            print()
        else:
            #userData = context['userData']
            processData = Process.objects.all()
            processData = initChapterNo(processData)
            context['processData'] = processData
            return render(request, 'process/process.html', context)
    else:
        return redirect('home')
