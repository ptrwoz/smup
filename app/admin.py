from django.contrib import admin
from django.apps import apps
from app.models import Rule
from app.models import Unit
from app.models import Process
from app.models import Employee
from app.models import Activity
from app.models import AuthUser
from app.models import Employeetype
#
models = apps.get_models()
admin.site.register(Rule)
admin.site.register(Unit)
admin.site.register(Process)
admin.site.register(Employee)
admin.site.register(Activity)
admin.site.register(AuthUser)
admin.site.register(Employeetype)