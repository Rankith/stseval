from django.contrib import admin
from management.models import Competition,Athlete,Judge,Session,Team,AthleteLevel,Disc,Event

# Register your models here.
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class AthleteLevelAdmin(admin.ModelAdmin):
    list_display=('id', 'disc','name','abbreviation')
    list_editable=('disc','name','abbreviation')
    list_filter=('disc',)

class EventAdmin(admin.ModelAdmin):
    list_display=('id', 'disc','name','full_name','display_order')
    list_editable=('disc','name','full_name','display_order')

admin.site.register(AthleteLevel,AthleteLevelAdmin)
admin.site.register(Event,EventAdmin)
admin.site.register(Disc)
admin.site.register(Competition)
admin.site.register(Judge)
admin.site.register(Athlete)
admin.site.register(Session)
admin.site.register(Team)
