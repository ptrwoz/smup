from app.view.activity import activityViews
from app.view.auth import authViews
from app.view.data import eporter
from app.view.importexport import importexportView
from app.view.main import mainViews
from django.urls import path
from app.view.process import processViews
from app.view.rule import ruleViews
from app.view.unit import unitViews

from app.view.user import userViews
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('login', authViews.loginPage, name='login'), #ok
    path('logout', authViews.logoutUser, name='logout'), #ok
    path('profil', authViews.profilUser, name='profil'), #ok

    path('users', userViews.usersView, name='users'),
    path('user/<str:id>', userViews.userView, name='user'),
    path('user', userViews.userView, name='user'),
    #
    path('units', unitViews.unitsView, name='units'),
    path('unit', unitViews.unitView, name='unit'),
    path('unit/<str:id>', unitViews.unitView, name='unit'),
    path('unit/<str:id>/<str:delete>', unitViews.unitView, name='unit'),
    #
    path('rule', ruleViews.ruleView, name='rule'),
    path('rule/<str:id>', ruleViews.ruleView, name='rule'),
    path('rules', ruleViews.rulesView, name='rules'),

    path('activities', activityViews.activityView, name='activities'),


    path('process', processViews.processView, name='process'),
    path('processes', processViews.processView, name='processes'),

    path('importexport', eporter.xlsxViewUnits, name='importexport'),
    path('export', importexportView.exportFile, name='export'),
    path('import', importexportView.importFile, name='import'),
    path('importExport', importexportView.importexportView, name='importExport'),

    path('', mainViews.home, name='home'),
]
urlpatterns += staticfiles_urlpatterns()