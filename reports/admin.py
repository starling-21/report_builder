from django.contrib import admin

from .models import Serviceman
from .models import Position
from .models import Rank
from .models import Unit

from .models import Report


class ReportAdmin(admin.ModelAdmin):
    # list_display = ("pk", "template_type")   #get_title_or_nothing"

    def get_form(self, request, obj=None, **kwargs):
        # if hasattr(obj, 'template_type') and obj.template_type == "regular_template":
        if obj is not None and obj.template_type == "regular_template":
            self.exclude = ("header_sample", "header_template", "footer_sample", "footer_template")
        form = super(ReportAdmin, self).get_form(request, obj, **kwargs)
        return form

# Register your models here.
admin.site.register(Serviceman)
admin.site.register(Position)
admin.site.register(Rank)
admin.site.register(Unit)
# admin.site.register(Report)


admin.site.register(Report, ReportAdmin)
