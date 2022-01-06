from django.contrib import messages
from django.shortcuts import render, redirect
from app.models import *
from app.view.auth.auth import authUser
from app.view.static.dataModels import UnitData
from app.view.static.messagesTexts import MESSAGES_ADD_ERROR, MESSAGES_NO_DATA, MESSAGES_OPERATION_SUCCESS, \
    MESSAGES_DATA_EXISTS, MESSAGES_OPERATION_ERROR, MESSAGES_USERINUNIT_ERROR, MESSAGES_DATA_ERROR
from app.view.static.urls import REDIRECT_HOME_URL, RENDER_UNITS_URL, REDIRECT_UNITS_URL, RENDER_UNIT_URL

#
# delete Unit
#
def deleteUnit(request, context, id=''):
    units = Unit.objects.filter(id_unit=id)
    if units.exists():
        unit = units[0]
        unitEmployeers = Employee.objects.filter(id_unit=id)
        if unitEmployeers.exists():
            messages.info(request, MESSAGES_USERINUNIT_ERROR, extra_tags='error')
            return redirect('../' + REDIRECT_UNITS_URL)
        try:
            unit.delete()
            messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')
            return redirect('../'+REDIRECT_UNITS_URL)
        except:
            messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
            return redirect('../'+REDIRECT_UNITS_URL)
    else:
        messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
        return redirect('../'+REDIRECT_UNITS_URL)

def checkUnitFromForm(request):
    unitName = request.POST.get('unitName')
    if len(unitName) == 0:
        unit = Unit()
        unit.name = unitName
        return None, MESSAGES_DATA_ERROR
    else:
        unit = Unit()
        unit.name = unitName
        return unit, None
#
#   update Unit
#
def updateUnit(request, context, id=''):
    newUnit, mess = checkUnitFromForm(request)
    if newUnit == None:
        messages.info(request, mess, extra_tags='error')
        return render(request, RENDER_UNIT_URL, context)
    units = Unit.objects.filter(id_unit=id)
    if units.exists():
        unit = units[0]
        context['unitData'] = unit
        if len(Unit.objects.filter(name=newUnit.name)) > 0:
            messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
            return render(request, RENDER_UNIT_URL, context)
        if Unit.objects.filter(name=newUnit.name).exists():
            messages.info(request, MESSAGES_DATA_EXISTS, extra_tags='error')
            return render(request, RENDER_UNIT_URL, context)
        try:
            unit.name = newUnit.name
            unit.save()
            messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')
            return redirect('../'+REDIRECT_UNITS_URL)
        except:
            messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
            return render(request, RENDER_UNIT_URL, context)
    else:
        messages.info(request, MESSAGES_ADD_ERROR)
        return render(request, RENDER_UNIT_URL, context)
#
#   save Unit
#
def saveUnit(request, context):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        unit, mess = checkUnitFromForm(request)
        if unit is None:
            messages.info(request, mess, extra_tags='error')
            return render(request, RENDER_UNIT_URL, context)
        newUnit = Unit()
        newUnit.name = unit.name
        try:
            newUnit.save()
            messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')
            return redirect('../'+REDIRECT_UNITS_URL)
        except:
            context['unitData'] = newUnit
            if len(Unit.objects.filter(name=unit.name)) > 0:
                messages.info(request, MESSAGES_DATA_EXISTS, extra_tags='error')
                return render(request, RENDER_UNIT_URL, context)

            messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
            return render(request, RENDER_UNIT_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)
#
#   view Unit
#
def viewUnit(request, context, id=''):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        if id == '':
            context['unitData'] = UnitData()
            return render(request, RENDER_UNIT_URL, context)
        elif id.isnumeric():
            units = Unit.objects.filter(id_unit=int(id))
            if units.exists():
                unit = units[0]
                context['unitData'] = unit
                return render(request, RENDER_UNIT_URL, context)
            else:
                return redirect('../'+REDIRECT_UNITS_URL)
        else:
            return redirect('../'+REDIRECT_UNITS_URL)
    else:
        return redirect(REDIRECT_HOME_URL)

#
#   main function
#
def unitManager(request, id='', operation=''):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        if request.method == 'POST':
            #update
            if len(id) > 0 and operation == '':
                return updateUnit(request, context, id)
            #delete
            elif len(id) > 0 and operation == 'delete':
                return deleteUnit(request, context, id)
            #save - new unit
            else:
                return saveUnit(request, context)
        else:
            #view
            return viewUnit(request, context, id)
    else:
        return redirect(REDIRECT_HOME_URL)

def countUnitEmployees(units):
    for u in units:
        u.countEmployees = len(Employee.objects.filter(id_unit = u.id_unit))
    return units
#
#   view units
#
def unitsView(request, field='name', sort='0'):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        if field == 'name' and sort == '0':
            units = Unit.objects.all().order_by('name')
        else:
            units = Unit.objects.all().order_by('-name')
        units = countUnitEmployees(units)
        context['units'] = units
        return render(request, RENDER_UNITS_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)
