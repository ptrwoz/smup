from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from ..models import *

def home(request):
    context = dict()
    if request.user.is_authenticated:
        context['logged'] = 'yes'
        userData = request.user
        employee = Employee.objects.filter(auth_user=userData.id)
        if (employee.exists()):
            context['userLabel'] = employee[0].name + " " + employee[0].surname
        else:
            context['userLabel'] = userData
    else:
        context['logged'] = 'no'
    return render(request, 'main/home.html', context)