from django.contrib import admin
from streaming.models import WowzaStream

# Register your models here.
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class WowzaStreamAdmin(admin.ModelAdmin):
    list_display=('id', 'stream_id','name','sdp_url','application_name','stream_name')

admin.site.register(WowzaStream,WowzaStreamAdmin)