from django.contrib import admin
from management.models import Competition,Athlete,Judge,Session,Team,AthleteLevel,Disc,Event,Sponsor,StartList,Camera

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
    list_display=('id', 'session','event','athlete','order','completed','active')
    list_editable=('order','completed','active')
    list_filter=('session','event')

admin.site.register(AthleteLevel,AthleteLevelAdmin)
admin.site.register(Event,EventAdmin)
admin.site.register(Disc,DiscAdmin)
admin.site.register(Competition)
admin.site.register(Judge)
admin.site.register(Athlete)
admin.site.register(Session)
admin.site.register(Team)
admin.site.register(Sponsor)
admin.site.register(Camera)
admin.site.register(StartList,StartListAdmin)
