from django.contrib import messages
from django.shortcuts import render, redirect
from app.models import *
from app.view.auth.auth import authUser
from app.view.static.dataModels import UnitData
from app.view.static.messagesTexts import MESSAGES_ADD_ERROR, MESSAGES_NO_DATA, MESSAGES_OPERATION_SUCCESS, \
    MESSAGES_DATA_EXISTS, MESSAGES_OPERATION_ERROR
from app.view.static.urls import REDIRECT_HOME_URL, RENDER_UNITS_URL, REDIRECT_UNITS_URL, RENDER_UNIT_URL

#
# delete Unit
#
def deleteUnit(request, context, id=''):
    users = Unit.objects.filter(idunit=id)
    if users.exists():
        try:
            users[0].delete()
            messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')
            return redirect('../'+REDIRECT_UNITS_URL)
        except:
            messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
            return redirect('../'+REDIRECT_UNITS_URL)
    else:
        messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')
        return redirect('../'+REDIRECT_UNITS_URL)

#
#   update Unit
#
def updateUnit(request, context, id=''):
    u = Unit.objects.filter(idunit=id)
    unitName = request.POST.get('unitName')
    if len(u) > 0:
        u = u[0]
        context['unitData'] = u
        if len(unitName) == 0:
            messages.info(request, MESSAGES_NO_DATA, extra_tags='error')
            return render(request, RENDER_UNIT_URL, context)
        if len(Unit.objects.filter(name=unitName)) > 0:
            messages.info(request, MESSAGES_DATA_EXISTS, extra_tags='error')
            return render(request, RENDER_UNIT_URL, context)
        try:
            u.name = unitName
            u.save()
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
        unitName = request.POST.get('unitName')
        newUnit = Unit()
        newUnit.name = unitName
        if len(unitName) == 0:
            messages.info(request, MESSAGES_OPERATION_ERROR, extra_tags='error')
            return render(request, RENDER_UNIT_URL, context)
        try:
            newUnit.save()
            messages.info(request, MESSAGES_OPERATION_SUCCESS, extra_tags='info')
            return redirect('../'+REDIRECT_UNITS_URL)

        except:
            context['unitData'] = newUnit
            if len(Unit.objects.filter(name=unitName)) > 0:
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
            units = Unit.objects.filter(idunit=int(id))
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
        context['units'] = units
        return render(request, RENDER_UNITS_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)
