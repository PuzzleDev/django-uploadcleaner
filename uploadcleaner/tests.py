'''
Copyright PuzzleDev s.n.c.
Created on Jul 14, 2012

@author: Michele Sama (m.sama@puzzledev.com)
'''
from django.test.testcases import TestCase
from uploadcleaner.models import UploadCleanerLog, UploadCleanerLogManager
from django.db import models
from uploadcleaner.utils import filefields_in_model, linked_files_from_model
from django.core.files.base import ContentFile

class NoFileModel(models.Model):
    name = models.SlugField()
    
class FileModel(NoFileModel):
    file = models.FileField(upload_to = "")
    image = models.ImageField(upload_to = "")


class UploadCleanerLogManagerTestCase(TestCase):
    
    def testFilterLinkedFiles(self):
        to_keep = ["a", "b", "c"]
        to_delete =  ["x", "y", "z"]
        all_files = to_delete + to_delete
        
        deleted = UploadCleanerLogManager()\
                .filter_linked_files(all_files, to_keep)
        self.assertEquals(to_delete, deleted)
        

class UtilsTestCase(TestCase):
        
    def testFileFieldsInModel(self):
        self.assertEqual([], filefields_in_model(NoFileModel))
        self.assertEqual(['file', 'image'],
                [x.name for x in filefields_in_model(FileModel)])
        
    def testLinkedFilesForModel(self):
        instance = UploadCleanerLog.objects.create()
        myfile = ContentFile("hello world")
        instance.log_file.save("hello.txt", myfile, save = True)
        instance.save()
        self.assertEqual(
                [instance.log_file.path,],
                linked_files_from_model(UploadCleanerLog))
        instance.delete()