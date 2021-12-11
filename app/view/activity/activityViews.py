from django.shortcuts import render, redirect
from app.models import Employee, Rule
from app.view.auth.auth import authUser
from app.view.static.urls import REDIRECT_HOME_URL, RENDER_ACTIVITY_URL

def activities(request):
    context = authUser(request)
    return render(request, RENDER_ACTIVITY_URL, context)
def activityView(request):
    context = authUser(request)
    if context['account'] != 'GUEST':
        # save and update
        if request.method == 'POST':
            print()
        elif request.method == 'DELETE':
            return redirect('home')
        # view user
        else:
            rules = Rule.objects.filter(employee_idemployee=context['userData'].id)
            context['rules'] = rules
            return render(request, RENDER_ACTIVITY_URL, context)
    else:
        return redirect(REDIRECT_HOME_URL)
