from django.contrib import admin
from app.models import Competition,Judge,Athlete,Twitch,Routine,EJuryDeduction
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class EJuryDeductionAdmin(ImportExportModelAdmin):
    list_display=('id', 'routine','judge','deduction','action','editor','time_stamp','time_stamp_relative','artistry_type')
    list_editable=('routine','judge','deduction','action','editor','time_stamp','time_stamp_relative','artistry_type')
    list_filter = ('routine__competition','routine__event')


admin.site.register(Competition)
admin.site.register(Judge)
admin.site.register(Athlete)
admin.site.register(Twitch)
admin.site.register(Routine)
admin.site.register(EJuryDeduction,EJuryDeductionAdmin)