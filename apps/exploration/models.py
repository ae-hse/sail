from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

import fca

class FAttribute(models.Model):
    """FObject stands for formal object"""
    name = models.CharField(_('name'), max_length=200, blank=False)
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
    name = models.CharField(_('name'), max_length=200, blank=False)
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
    
    def get_as_boolean_list(self, group):
        """Return a list which represents what attributes this object has"""
        object_intent = self.attributes.all()
        all_attributes = group.content_objects(FAttribute)
        return [(attr in object_intent) for attr in all_attributes]

class AttributeImplication(models.Model):
    """Implication on attributes in background knowledge"""
    premise = models.ManyToManyField(FAttribute, related_name='premise_set+')
    conclusion = models.ManyToManyField(FAttribute, related_name='conclusion_set+')
    minimal_generator = models.ManyToManyField(FAttribute, related_name='mingen_set+')

    # The following three fields are required for being group aware.
    # We use a nullable generic foreign key to enable it to be optional
    # and we don't know what group model it will point to.
    object_id = models.IntegerField(null=True)
    content_type = models.ForeignKey(ContentType, null=True)
    group = generic.GenericForeignKey("content_type", "object_id")

    def get_premise(self):
        return set([attr.pk for attr in self.premise.all()])
        
    def get_conclusion(self):
        return set([attr.pk for attr in self.conclusion.all()])

    def get_as_fca_implication(self):
        return fca.Implication(set([attr.name for attr in self.premise.all()]), 
                               set([attr.name for attr in self.conclusion.all()]))