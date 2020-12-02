from django.contrib import admin
from app.models import Routine,EJuryDeduction,BackupVideo
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class EJuryDeductionAdmin(ImportExportModelAdmin):
    list_display=('id', 'routine','judge','deduction','action','editor','time_stamp','time_stamp_relative','artistry_type')
    list_editable=('routine','judge','deduction','action','editor','time_stamp','time_stamp_relative','artistry_type')
    list_filter = ('routine__session__competition','routine__event')

class RoutineAdmin(ImportExportModelAdmin):
    list_display=('id', 'event','athlete','status')
    list_filter = ('session','event')

class BackupVideoAdmin(ImportExportModelAdmin):
    list_display=('id','session','event','athlete','reviewed','video_file')
    list_editable=('reviewed',)
    list_filter = ('session','event')

admin.site.register(Routine,RoutineAdmin)
admin.site.register(EJuryDeduction,EJuryDeductionAdmin)
admin.site.register(BackupVideo,BackupVideoAdmin)