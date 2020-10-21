from django.contrib import admin
from management.models import Competition,Athlete,Judge,Session

# Register your models here.
from import_export import resources
from import_export.admin import ImportExportModelAdmin


admin.site.register(Competition)
admin.site.register(Judge)
admin.site.register(Athlete)
admin.site.register(Session)
