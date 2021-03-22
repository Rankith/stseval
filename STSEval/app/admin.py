from django.contrib import admin
from app.models import Routine,EJuryDeduction,BackupVideo,DJuryIndicator,ConversionSetting
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class EJuryDeductionAdmin(ImportExportModelAdmin):
    list_display=('id', 'routine','judge','deduction','action','editor','time_stamp','time_stamp_relative','artistry_type')
    list_editable=('routine','judge','deduction','action','editor','time_stamp','time_stamp_relative','artistry_type')
    list_filter = ('routine__session__competition','routine__event')

class RoutineAdmin(ImportExportModelAdmin):
    list_display=('id', 'event','athlete','status','video_converted','video_saved')
    list_editable=('status','video_converted','video_saved')
    list_filter = ('session','event','video_converted')

class BackupVideoAdmin(ImportExportModelAdmin):
    list_display=('id','session','event','athlete','converted','reviewed','video_file','job_id')
    list_editable=('converted','reviewed')
    list_filter = ('session','event')

class DJuryIndicatorAdmin(ImportExportModelAdmin):
    list_display=('id', 'routine','type','value','time_stamp_relative')
    list_editable=('routine','type','value','time_stamp_relative')
    list_filter = ('routine__session__competition','routine__event','type')

class ConversionSettingAdmin(ImportExportModelAdmin):
    list_display=('id', 'do_conversions')
    list_editable=('do_conversions',)

admin.site.register(Routine,RoutineAdmin)
admin.site.register(EJuryDeduction,EJuryDeductionAdmin)
admin.site.register(BackupVideo,BackupVideoAdmin)
admin.site.register(DJuryIndicator,DJuryIndicatorAdmin)
admin.site.register(ConversionSetting,ConversionSettingAdmin)