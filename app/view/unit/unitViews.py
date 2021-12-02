from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from app.models import *
from django.contrib import messages
from app.view.auth.auth import authUser

class UnitData:
    id = ""
    name = ""
    pass

def deleteUnit(request, context, id):
    u = Unit.objects.filter(idunit=id)
    if len(u) > 0:
        try:
            us = u[0].delete()
            print()
        except:
            context["errorMessages"] = 1
            messages.info(request, 'Błąd usunięcia')
            return redirect('units')
    context["errorMessages"] = 0
    messages.info(request, 'Usunięto dane')
    return redirect('units')
def saveUnit(request, context, id):
    unitName = request.POST.get('unitName')
    u = Unit()
    u.name = unitName
    try:
        us = Unit.objects.filter(idunit=id)
        if len(us) > 0:
            us = us[0]
            us.name = unitName
            us.save()
        else:
            u.save()
        context['unitData'] = u
        return redirect('unit/' + str(u.idunit))
    except:
        messages.info(request, 'Błąd dodania')
        return render(request, 'unit/unit.html', context)

def viewUnit(request, context, id):
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        if len(id) == 0:
            context['unitData'] = UnitData()
            return render(request, 'unit/unit.html', context)
        elif len(id) > 0 and id.isnumeric():
            u = Unit.objects.filter(idunit=int(id))
            if len(u) > 0:
                u = u[0]
                context['unitData'] = u
                return render(request, 'unit/unit.html', context)
            else:
                return redirect('units')
        else:
            return render(request, 'unit/units.html', context)
    else:
        return redirect('home')


def unitView(request, id = '', delete = ''):
    context = authUser(request)
    if request.method == 'POST':
        return saveUnit(request, context, id)
    elif delete == 'delete':
        return deleteUnit(request, context, id)
    else:
        return viewUnit(request, context, id)

def unitsView(request, field = 'name',sort = ''):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        if (field == 'name' and sort == "0"):
            units = Unit.objects.all().order_by('name')
        else:
            units = Unit.objects.all().order_by('-name')
        context['units'] = units
        return render(request, 'unit/units.html', context)
    else:
        return redirect('home')
