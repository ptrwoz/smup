from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from ..models import *


def home(request):
    context = dict()
    if request.user.is_authenticated:
        userData = request.user
        employee = Employee.objects.filter(auth_user=userData.id)
        if employee.exists():
            context['userLabel'] = employee[0].name + " " + employee[0].surname
            context['account'] = str(employee[0].idemployeetype.name)
        else:
            context['userLabel'] = userData
            context['account'] = 'null'
    else:
        context['account'] = 'null'
    return render(request, 'main/home.html', context)
