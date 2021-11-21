from datetime import datetime
from datetime import timedelta
from openpyxl import Workbook
from django.http import HttpResponse

from ..models import *

class Exporter:
    def function(self):
        return 1