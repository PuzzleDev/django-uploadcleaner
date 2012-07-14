'''
Created on Sep 23, 2011

@author: Michele Sama (m.sama@puzzledev.com)
'''
import datetime
import os
from zipfile import ZipFile

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import loading
from django.db.models.base import Model
from django.db.models.fields.files import FileField


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
        
        Usage: clean_obsolete_uploads [dryrun] [backup]
        dryrun: only list obsolete files without deleting them
        backup: create a zip file with all the obsolete files
    """
    
    help = 'Removes all the uploaded files which are not saved in the database'


    def handle(self, *args, **options):
        dryrun = True if "dryrun" in args else False
        backup = True if "backup" in args else False

        # List all the media files        
        files_on_filesystem = []
        if hasattr(settings, 'MEDIA_FOLDER_LIST'):
            for folder in settings.MEDIA_FOLDER_LIST:
                files_on_filesystem += self.__get_files(folder)
        else:
            files_on_filesystem = self.__get_files(settings.MEDIA_ROOT)
 
        # List all the files linked in the DB
        files_on_db =  self.__get_file_from_db()
        
        # Flag as obsolete all the files in (filesystem - db) 
        obsolete = [x 
                for x in files_on_filesystem
                if x not in files_on_db]    
        
        # Create backup
        if backup:        
            backup_filename = os.path.join(settings.MEDIA_ROOT,
                    "obsolete_uploads/" + 
                    datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + 
                    ".zip")
            backup = ZipFile(backup_filename,"w")
            for filename in obsolete:
                backup.write(filename)
            backup.close()
                
        if not dryrun:         
            log_filename = os.path.join(settings.MEDIA_ROOT,
                    "obsolete_uploads/" +
                    datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") +
                    ".log")
            
            log = open(log_filename, "w")
            for filename in obsolete:
                log_string = "removing: %s" % filename
                print log_string
                log.write(log_string + "\n")
                os.remove(file)
            log.close()
        else:
            # Dry run - just write 
            for filename in obsolete:
                print "obsolete: %s" % filename


    def __get_files(self, media_folder):
        """ List all the files in all the subfolders
            of the given folder.
        """
        found_files = []
        for root, dirnames, filenames in os.walk(media_folder):
            filenames = [os.path.join(root, x) for x in filenames]
            filenames = [x for x in filenames if os.path.isfile(x)]
            for filename in filenames:
                found_files.append(os.path.abspath(unicode(filename)))
        return found_files


    def __get_file_from_db(self):
        """ List all the files in all the tables.
        """
        models = loading.get_models()
        files = []
        
        for model_class in models:
            fields = self.__get_model_filefields(model_class)
            instances = model_class.objects.all()
            for instance in instances:
                for field in fields:
                    value = getattr(instance, field[0])
                    if value.name:
                        files.append(os.path.abspath(value.path))
        return files
    
    
    def __get_model_filefields(self, model):
        """ Get all the file fields of the given model
        """
        if not issubclass(model, Model):
            raise CommandError(
                    "%s should be a Model subclass" % model)
        
        fields = model._meta.fields
        fields = [(x.name, x)
                for x in fields
                if isinstance(x, FileField)]
        return fields      
        