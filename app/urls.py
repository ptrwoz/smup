from app.auth import authViews
from app.main import mainViews
from django.urls import path, include # new
from django.conf.urls import handler404
from app.process import processViews
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('login', authViews.loginPage, name='login'),
    path('logout', authViews.logoutUser, name='logout'),
    path('profil', authViews.profilUser, name='profil'),
    path('process', processViews.processView, name='process'),
    path('', mainViews.home, name='home'),
]
urlpatterns += staticfiles_urlpatterns()