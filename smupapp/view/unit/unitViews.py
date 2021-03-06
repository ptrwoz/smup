from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render, redirect
from smupapp.models import *
from smupapp.view.auth.auth import authUser
from smupapp.view.static.dataModels import UnitData
from smupapp.view.static.messagesTexts import MESSAGES_ADD_ERROR, MESSAGES_NO_DATA, MESSAGES_OPERATION_SUCCESS, \
    MESSAGES_DATA_EXISTS, MESSAGES_OPERATION_ERROR, MESSAGES_USERINUNIT_ERROR, MESSAGES_DATA_ERROR
from smupapp.view.static.staticValues import USER_ACCOUNT
from smupapp.view.static.urls import REDIRECT_HOME_URL, RENDER_UNITS_URL, REDIRECT_UNITS_URL, RENDER_UNIT_URL

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
        unit.is_active = 1
        return None, MESSAGES_DATA_ERROR
    else:
        unit = Unit()
        unit.name = unitName
        unit.is_active = 1
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
            unit.is_active = 1
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
            if operation == 'active':
                return unitActive(request, id)
            #view
            return viewUnit(request, context, id)
    else:
        return redirect(REDIRECT_HOME_URL)

def countUnitEmployees(units):
    for u in units:
        u.countEmployees = len(Employee.objects.filter(id_unit = u.id_unit))
    return units

def getUnitsToEdit(userRole):
    units = Unit.objects.all().order_by('name')
    for unit in units:
        if unit.is_active:
            unit.editable = True
        elif userRole == 'ADMIN':
            unit.editable = True
        else:
            unit.editable = False
    '''if userRole == 'ADMIN':
        units = Unit.objects.all().order_by('name')
    elif userRole == 'PROCESS MANAGER' or userRole == 'MANAGER':
        units = Unit.objects.filter(Q(is_active = 1)).order_by('name')
    else:
        units = None'''
    return units
#
#   view units
#
def unitsView(request, field='name', sort='0'):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        units = getUnitsToEdit(context[USER_ACCOUNT])

        '''if field == 'name' and sort == '0':
            units = Unit.objects.all().order_by('name')
        else:
            units = Unit.objects.all().order_by('-name')'''
        units = countUnitEmployees(units)

        page = request.GET.get('page', 1)
        paginator = Paginator(units, 10)
        try:
            units = paginator.page(page)
        except PageNotAnInteger:
            units = paginator.page(1)
        except EmptyPage:
            units = paginator.page(paginator.num_pages)

        context['units'] = units
        return render(request, RENDER_UNITS_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)
#
#   unit change active
#
def unitActive(request, id=''):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER': #or context['account'] == 'MANAGER'
        if len(id) > 0:
            units = Unit.objects.filter(id_unit=int(id))
            if units is not None:
                u = units[0]
                if u.is_active == 1:
                    u.is_active = 0
                else:
                    u.is_active = 1
                u.save()
                return redirect(REDIRECT_UNITS_URL)
            else:
                return redirect(REDIRECT_UNITS_URL)
    else:
        return redirect(REDIRECT_HOME_URL)