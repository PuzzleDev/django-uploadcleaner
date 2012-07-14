'''
Created on Sep 23, 2011

@author: Michele Sama (m.sama@puzzledev.com)
'''
from django.core.management.base import BaseCommand

from uploadcleaner.models import UploadCleanerLog

class Command(BaseCommand):
    """ clean_obsolete_uploads lists all the files contained in the
        database and all the files in the media folders and 
        DELETES all those files which are no longer in the database.
        
        Since django 1.3 deleting a FileField does not delete the
        linked file. Such files remain in the filesystem and need to
        be deleted manually. 
        
        Files are loaded from a settings.MEDIA_FOLDER_LIST list
        of folders. If that is not defined settings.MEDIA_ROOT
        is used instead. 
        
        Logs and backups are stored in
        settings.MEDIA_ROOT + "cleaned_obsolete_uploads/".
        Files in that folder are not deleted.
        
        Usage: clean_obsolete_uploads [dryrun] [backup]
        dryrun: only list obsolete files without deleting them
        backup: create a zip file with all the obsolete files
    """
    help = 'Removes all the uploaded files which are not saved in the database'

    def handle(self, *args, **options):
        dryrun = True if "dryrun" in args else False
        backup = True if "backup" in args else False
        UploadCleanerLog.objects.do_clean(backup, dryrun)