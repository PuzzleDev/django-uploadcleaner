'''
Created on Sep 23, 2011

@author: Michele Sama (m.sama@puzzledev.com)
'''
import datetime
import os
from zipfile import ZipFile

from django.conf import settings
from django.core.management.base import BaseCommand

from uploadcleaner.utils import files_at_path,\
    linked_files_from_all_models


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

    log_folder = os.path.join(settings.MEDIA_ROOT,
            "cleaned_obsolete_uploads/")

    def handle(self, *args, **options):
        dryrun = True if "dryrun" in args else False
        backup = True if "backup" in args else False


        files_on_filesystem = self.files_from_upload_paths()
        files_on_db =  linked_files_from_all_models()
        
        obsolete_files = self.filter_linked_files(
                files_on_filesystem, files_on_db)
        
        # Create backup
        if backup:        
            self.create_backup(obsolete_files)
        
        if dryrun:
            self.dryrun(obsolete_files)
        else:       
            self.delete_obsolete_files(obsolete_files)
        
    
    def files_from_upload_paths(self):
        """ Creates a list with all the files in the
            defined upload folders.
        """
        if hasattr(settings, 'MEDIA_FOLDER_LIST'):
            print("Fetching files from %s" %
                  settings.MEDIA_FOLDER_LIST)
            upload_paths = settings.MEDIA_FOLDER_LIST
        else:
            print("settings.MEDIA_FOLDER_LIST is not set.")
            print("Fetching files from %s" %
                  settings.MEDIA_ROOT)
            upload_paths = (settings.MEDIA_ROOT,)
            
        files_on_filesystem = []
        for folder in upload_paths:
            files_on_filesystem += files_at_path(folder)
        return files_on_filesystem


    def filter_linked_files(self,
            files_on_filesystem, files_on_db):
        """ Given the list of all the files in the upload path
            filter those files which are linked by the database
            and those which are in the log directory.
        """
        return [x 
            for x in files_on_filesystem
            if x not in files_on_db
                and not x.startswith(self.log_folder)]
        
            
    def create_backup(self, files):
        backup_filename = os.path.join(
                self.log_folder + 
                datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + 
                ".zip")
        backup = ZipFile(backup_filename,"w")
        for filename in files:
            backup.write(filename)
        backup.close()


    def dryrun(self, files):
        """ Print the list of obsolete files without
            deleting them.
        """
        for filename in files:
            print "dryrun: %s" % filename  


    def delete_obsolete_files(self, files):
        """ Delete all the obsolete files and save
            their name in a log file.
        """
        log_filename = os.path.join(
                self.log_folder + 
                datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") +
                ".log")
        
        log = open(log_filename, "w")
        for filename in files:
            log_string = "removing: %s" % filename
            print(log_string)
            log.write(log_string + "\n")
            os.remove(file)
        log.close()