from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

class FAttribute(models.Model):
    """FObject stands for formal object"""
    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), blank=True)

    # we can built hierarchies of objects
    # parent in the sense of type or class
    parent = models.ForeignKey('self', 
                              blank=True, 
                              null=True)
                              
    # The following three fields are required for being group aware.
    # We use a nullable generic foreign key to enable it to be optional
    # and we don't know what group model it will point to.
    object_id = models.IntegerField(null=True)
    content_type = models.ForeignKey(ContentType, null=True)
    group = generic.GenericForeignKey("content_type", "object_id")

    def __unicode__(self):
      return self.name

class FObject(models.Model):
    """FObject stands for formal object"""
    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    attributes = models.ManyToManyField(FAttribute, blank=True)
    
    # we can built hierarchies of objects
    # parent in the sense of type or class
    parent = models.ForeignKey('self', 
                               blank=True, 
                               null=True)
                               
    # The following three fields are required for being group aware.
    # We use a nullable generic foreign key to enable it to be optional
    # and we don't know what group model it will point to.
    object_id = models.IntegerField(null=True)
    content_type = models.ForeignKey(ContentType, null=True)
    group = generic.GenericForeignKey("content_type", "object_id")
    
    def __unicode__(self):
        return self.name
        
    def has_attributes(self, attributes):
        for attr in attributes:
            if len(self.attributes.filter(name=attr)) == 0:
                return False
        return True