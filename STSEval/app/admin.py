from django.contrib import admin
from app.models import Routine,EJuryDeduction
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class EJuryDeductionAdmin(ImportExportModelAdmin):
    list_display=('id', 'routine','judge','deduction','action','editor','time_stamp','time_stamp_relative','artistry_type')
    list_editable=('routine','judge','deduction','action','editor','time_stamp','time_stamp_relative','artistry_type')
    list_filter = ('routine__session__competition','routine__event')

admin.site.register(Routine)
admin.site.register(EJuryDeduction,EJuryDeductionAdmin)