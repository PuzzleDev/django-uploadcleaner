django-uploadcleaner
====================

clean_obsolete_uploads lists all the files contained in the
database and all the files in the media folders and 
DELETES all those files which are no longer in the database.
        
Since django 1.3 deleting a FileField does not delete the
linked file. Such files remain in the filesystem and need to
be deleted manually. 
        
Files are loaded from a settings.MEDIA_FOLDER_LIST list
of folders. If that is not defined settings.MEDIA_ROOT
is used instead. 
        
Usage: clean_obsolete_uploads [dryrun] [backup]
dryrun: only list obsolete files without deleting them
backup: create a zip file with all the obsolete files