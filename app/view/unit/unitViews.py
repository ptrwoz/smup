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
    print()
def saveUnit(request, context, id):
    print()
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


def unitView(request, id):
    context = authUser(request)
    if request.method == 'POST':
        return print()
    elif request.method == 'DELETE':
        return deleteUnit(request, context, id)
        print()
    else:
        return viewUnit(request, context, id)

def unitsView(request, field = 'name',sort = '0'):
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
