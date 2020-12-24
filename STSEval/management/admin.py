from django.contrib import admin
from management.models import Competition,Athlete,Judge,Session,Team,AthleteLevel,Disc,Event,Sponsor,StartList,Camera,RotationOrder

# Register your models here.
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class AthleteLevelAdmin(ImportExportModelAdmin):
    list_display=('id', 'disc','name','abbreviation','order','scoring_type')
    list_editable=('disc','name','abbreviation','order','scoring_type')
    list_filter=('disc','scoring_type')

class EventAdmin(ImportExportModelAdmin):
    list_display=('id', 'disc','name','full_name','display_order')
    list_editable=('disc','name','full_name','display_order')

class DiscAdmin(ImportExportModelAdmin):
    list_display=('id', 'name','full_name','active','display_order')
    list_editable=('name','full_name','active','display_order')

class StartListAdmin(ImportExportModelAdmin):
    list_display=('id', 'session','event','athlete','order','completed','active','secondary_judging')
    list_editable=('order','completed','active','secondary_judging')
    list_filter=('session','event')

class JudgeAdmin(ImportExportModelAdmin):
    list_display=('id', 'session','event','d1_email','d2_email','e1_email','e2_email','e3_email','e4_email')
    list_display=('session','event','d1_email','d2_email','e1_email','e2_email','e3_email','e4_email')
    list_filter=('session','event')

class RotationOrderAdmin(ImportExportModelAdmin):
    list_display=('id', 'session','rotation','event','order')
    list_editable=('order',)
    list_filter=('session','event','rotation')

class SessionAdmin(ImportExportModelAdmin):
    list_display=('id','name','active','paid','finished','payment_intent')
    list_editable=('active','paid','finished','payment_intent')
    list_filter=('competition__disc','active','finished')

admin.site.register(AthleteLevel,AthleteLevelAdmin)
admin.site.register(Event,EventAdmin)
admin.site.register(Disc,DiscAdmin)
admin.site.register(Competition)
admin.site.register(Judge,JudgeAdmin)
admin.site.register(Athlete)
admin.site.register(Session,SessionAdmin)
admin.site.register(Team)
admin.site.register(Sponsor)
admin.site.register(Camera)
admin.site.register(StartList,StartListAdmin)
admin.site.register(RotationOrder,RotationOrderAdmin)
