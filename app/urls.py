from django.urls import path
from app.auth import authViews
from app.main import mainViews
from django.urls import path, include # new

urlpatterns = [
    path('login', authViews.loginPage, name='login'),
    path('logout', authViews.logoutUser, name='logout'),
    path('profil', authViews.profilUser, name='profil'),

    path('', mainViews.home, name='home'),
]