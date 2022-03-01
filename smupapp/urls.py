from smupapp.view.activity import activityViews
from smupapp.view.auth import authViews
from smupapp.view.importexport import importexportViews
from smupapp.view.main import mainViews
from django.urls import path
from smupapp.view.process import processViews
from smupapp.view.rule import ruleViews
from smupapp.view.unit import unitViews

from smupapp.view.user import userViews
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('login', authViews.loginPage, name='login'), #ok
    path('logout', authViews.logoutUser, name='logout'), #ok
    path('profil', authViews.profilUserView, name='profil'), #ok
    path('profil/password', authViews.changePasswordView, name='password'), #ok

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
    path('export', importexportViews.exportFile, name='export'),
    path('import', importexportViews.importFile, name='import'),
    path('importExport', importexportViews.importexportManager, name='importExport'),
    path('backup', importexportViews.backup, name='backup'),
    path('', mainViews.home, name='home'),
]
urlpatterns += staticfiles_urlpatterns()