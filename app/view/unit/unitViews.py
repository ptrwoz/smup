from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from app.models import *
from django.contrib import messages

class UnitData:
    id = ""
    name = ""
    pass

def viewUnit(request, id):
    context = dict()
    unitData = UnitData()
    if request.user.is_authenticated:
        userData = request.user
        employee = Employee.objects.filter(auth_user=userData.id)
        if employee.exists():
            context['userLabel'] = employee[0].name + " " + employee[0].surname
            context['account'] = str(employee[0].idemployeetype.name)
            if id != "":
                try:
                    units = Unit.objects.filter(idunit=int(id))
                    if len(units) >= 1:
                        if request.method == 'POST':
                            unitName = request.POST.get('unitName')
                            units[0].name = unitName
                            units[0].save()
                            messages.info(request, 'Zapisano!')
                            return redirect('../units/' + id)
                            #return render(request, 'unit/unit/' + id +  '.html', context)
                        else:
                            unitData.name = units[0].name
                            unitData.idunit = units[0].idunit
                            context['unitData'] = unitData
                            context['userData'] = userData
                            return render(request, 'unit/unit.html', context)
                    elif int(id) == -1:
                        if request.method == 'POST':
                            unitName = request.POST.get('unitName')
                            units = Unit()
                            units[0].name = unitName
                            units[0].save()
                            messages.info(request, 'Zapisano!')
                            return redirect('../units/' + id)
                            #return render(request, 'unit/unit/' + id +  '.html', context)
                        else:
                            context['unitData'] = unitData
                            context['userData'] = userData
                            return render(request, 'unit/unit.html', context)
                    else:
                        return redirect('../')
                except Exception as e:
                    return render(request, 'unit/units.html', context)
                else:
                    return render(request, 'unit/units.html', context)
            else:
                return render(request, 'unit/unit.html', context)
        else:
            context['userLabel'] = userData
            context['account'] = 'GUEST'
            return redirect('../main/home.html')
    else:
        context['account'] = 'GUEST'
        return redirect('main/home.html')
    return redirect('main/home.html')

def viewUnits(request,field = 'name',sort = '0'):
    context = dict()
    if request.user.is_authenticated:
        userData = request.user
        employee = Employee.objects.filter(auth_user=userData.id)
        if employee.exists():
            context['userLabel'] = employee[0].name + " " + employee[0].surname
            context['account'] = str(employee[0].idemployeetype.name)
        else:
            context['userLabel'] = userData
            context['account'] = 'GUEST'
        if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER':
            if(field == 'name' and sort == "0"):
                units = Unit.objects.all().order_by('name')
            else:
                units = Unit.objects.all().order_by('-name')
            context['units'] = units
            return render(request, 'unit/units.html', context)
    else:
        context['account'] = 'GUEST'
        return render(request, 'main/home.html', context)
    return redirect('main/home.html')
