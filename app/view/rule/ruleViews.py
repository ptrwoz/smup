from django.shortcuts import render, redirect

from app.models import Rule
from app.view.auth.auth import authUser


def rulesView(request):
    context = authUser(request)
    if context['account'] == 'ADMIN' or context['account'] == 'PROCESS MANAGER' or context['account'] == 'MANAGER':
        rules = Rule.objects.all()
        context['rules'] = rules
        return render(request, 'rule/rules.html', context)
    else:
        return redirect('home')