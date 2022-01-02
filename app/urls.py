from app.view.activity import activityViews
from app.view.auth import authViews
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
    #
    path('users', userViews.usersView, name='users'),
    path('user/<str:id>', userViews.userManager, name='user'),
    path('user/<str:id>/<str:operation>', userViews.userManager, name='user'),
    path('user', userViews.userManager, name='user'),
    # ok
    path('units/<str:field>/<str:sort>', unitViews.unitsView, name='units'),
    path('units', unitViews.unitsView, name='units'),
    path('unit', unitViews.unitManager, name='unit'),
    path('unit/<str:id>', unitViews.unitManager, name='unit'),
    path('unit/<str:id>/<str:operation>', unitViews.unitManager, name='unit'),
    #rules urls
    path('rules', ruleViews.rulesView, name='rules'), #view all
    path('rule', ruleViews.ruleManager, name='rule'), #view new rule
    path('rule/<str:id>', ruleViews.ruleManager, name='rule'), #view existed rule
    path('rule/<str:id>/<str:operation>', ruleViews.ruleManager, name='rule'), #update, delete rule by operation

    path('activities', activityViews.activitiesView, name='activities'),
    path('activity/<str:id>', activityViews.activitiesManager, name='activities'),

    path('process', processViews.processView, name='process'),
    path('processes', processViews.processView, name='processes'),

    #path('importexport', eporter.xlsxViewUnits, name='importexport'),
    path('export', importexportView.exportFile, name='export'),
    path('import', importexportView.importFile, name='import'),
    path('importExport', importexportView.importexportView, name='importExport'),

    path('', mainViews.home, name='home'),
]
urlpatterns += staticfiles_urlpatterns()