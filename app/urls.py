from app.view.activity import activityViews
from app.view.auth import authViews
from app.view.main import mainViews
from django.urls import path
from app.view.process import processViews
from app.view.unit import unitViews
from app.view.user import userViews
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from app.xlsxmanager import Exporter

urlpatterns = [
    path('login', authViews.loginPage, name='login'),
    path('logout', authViews.logoutUser, name='logout'),
    path('profil', authViews.profilUser, name='profil'),
    path('activities', activityViews.activityView, name='activities'),
    path('users', userViews.usersView, name='users'),
    path('user/<str:id>', userViews.userView, name='users'),
    path('process', processViews.processView, name='process'),
    #path('units/<str:field>;<str:sort>', unitViews.viewUnits, name='units'),
    path('units', unitViews.viewUnits, name='units'),
    path('units/<str:id>', unitViews.viewUnit, name='unit'),
    path('excelTest', Exporter.generateExcelgenerateExcel, name='excelTest'),
    path('xlsxViewUnits', Exporter.xlsxViewUnits, name='xlsxViewUnits'),
    path('export', Exporter.exportFile, name='export'),
    path('', mainViews.home, name='home'),
]
urlpatterns += staticfiles_urlpatterns()