'''
Copyright PuzzleDev s.n.c.
Created on Jul 14, 2012

@author: Michele Sama (m.sama@puzzledev.com)
'''
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.test.testcases import TestCase

from uploadcleaner.models import UploadCleanerLog, UploadCleanerLogManager
from uploadcleaner.utils import filefields_in_model, linked_files_from_model


class UploadCleanerLogManagerTestCase(TestCase):
    
    def testFilterLinkedFiles(self):
        to_keep = ["a", "b", "c"]
        to_delete =  ["x", "y", "z"]
        all_files = to_keep + to_delete
        
        deleted = UploadCleanerLogManager()\
                .filter_linked_files(all_files, to_keep)
        self.assertEquals(to_delete, deleted)
        

class UtilsTestCase(TestCase):
        
    def testFileFieldsInModel(self):
        self.assertEqual([], filefields_in_model(User))
        self.assertEqual(['log_file', 'backup_file'],
                [x.name for x in filefields_in_model(UploadCleanerLog)])
        
    def testLinkedFilesForModel(self):
        instance = UploadCleanerLog.objects.create()
        myfile = ContentFile("hello world")
        instance.log_file.save("hello.txt", myfile, save = True)
        instance.save()
        self.assertEqual(
                [instance.log_file.path,],
                linked_files_from_model(UploadCleanerLog))
        instance.delete()