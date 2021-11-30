from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app.models import Employee, Rule
from app.models import Process
from app.models import RuleHasProcess
import datetime
from app.view.auth.auth import authUser


def activityView(request):
    context = authUser(request)
    if context['account'] != 'GUEST':
        # save and update
        if request.method == 'POST':
            print()
            #return saveUser(request, context, id)
        elif request.method == 'DELETE':
            return redirect('home')
        # view user
        else:
            rules = Rule.objects.filter(employee_idemployee = context['userData'].id)
            context['rules'] = rules
            return render(request, 'activity/activities.html', context)
    else:
        return redirect('home')
