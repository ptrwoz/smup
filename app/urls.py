from django.urls import path
from app.auth import authViews
from app.main import mainViews

urlpatterns = [
    path('login', authViews.login, name='login'),
    path('', mainViews.index, name='index'),
]