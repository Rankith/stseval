from django.contrib import admin
from management.models import Competition,Athlete,Judge,Session,Team,AthleteLevel

# Register your models here.
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class AthleteLevelAdmin(admin.ModelAdmin):
    list_display=('id', 'disc','name','abbreviation')
    list_editable=('disc','name','abbreviation')
    list_filter=('disc',)

admin.site.register(AthleteLevel,AthleteLevelAdmin)

admin.site.register(Competition)
admin.site.register(Judge)
admin.site.register(Athlete)
admin.site.register(Session)
admin.site.register(Team)
