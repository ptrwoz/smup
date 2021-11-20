from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

def login(request):
    return render(request, 'auth/login.html')