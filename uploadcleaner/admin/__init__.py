from django.contrib import admin

from uploadcleaner.models import UploadCleanerLog

class UploadCleanerLogAdmin(admin.ModelAdmin):
    list_display = (
            'timestamp',
            'dryrun',
            )
    
    readonly_fields = (
            'timestamp',
            'dryrun',
            'log_file',
            'backup_file',
            )

    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True
    

admin.site.register(UploadCleanerLog, UploadCleanerLogAdmin)