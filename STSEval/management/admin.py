from django.contrib import admin
from management.models import Competition,Athlete,Judge,Session,Team,AthleteLevel,Disc,Event,Sponsor,StartList,Camera,RotationOrder,AthleteAge

# Register your models here.
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class AthleteAdmin(ImportExportModelAdmin):
    list_display=('id','name','team','level','age','rotation')
    list_editable=('name','rotation')
    list_filter=('team','team__session')

class AthleteLevelAdmin(ImportExportModelAdmin):
    list_display=('id', 'disc','name','abbreviation','order','scoring_type')
    list_editable=('disc','name','abbreviation','order','scoring_type')
    list_filter=('disc','scoring_type')

class AthleteAgeAdmin(ImportExportModelAdmin):
    list_display=('id', 'athlete_level','name','order')
    list_editable=('athlete_level','name','order')
    list_filter=('athlete_level__disc','athlete_level')

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
    list_display=('id','name','active','paid','finished','admin_test_mode','free','payment_intent')
    list_editable=('active','paid','finished','admin_test_mode','free','payment_intent')
    list_filter=('competition__disc','active','finished')

admin.site.register(AthleteLevel,AthleteLevelAdmin)
admin.site.register(AthleteAge,AthleteAgeAdmin)
admin.site.register(Event,EventAdmin)
admin.site.register(Disc,DiscAdmin)
admin.site.register(Competition)
admin.site.register(Judge,JudgeAdmin)
admin.site.register(Athlete,AthleteAdmin)
admin.site.register(Session,SessionAdmin)
admin.site.register(Team)
admin.site.register(Sponsor)
admin.site.register(Camera)
admin.site.register(StartList,StartListAdmin)
admin.site.register(RotationOrder,RotationOrderAdmin)
