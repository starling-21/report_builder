from django.contrib import admin

from .models import Serviceman
from .models import Position
from .models import Rank
from .models import Unit

from .models import Report

# Register your models here.
admin.site.register(Serviceman)
admin.site.register(Position)
admin.site.register(Rank)
admin.site.register(Unit)
admin.site.register(Report)
