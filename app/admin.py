from django.contrib import admin
from django.apps import apps
from .models import *
#
models = apps.get_models()
admin.site.register(Rule)
admin.site.register(Unit)
admin.site.register(Process)
admin.site.register(Employee)
admin.site.register(Activity)
admin.site.register(AuthUser)
admin.site.register(Employeetype)