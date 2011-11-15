#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.db.models import signals

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
    
    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("context_new_object", 
                                        "New Object was created", 
                                        "new object was created in one of your projects")
        notification.create_notice_type("context_new_attribute", 
                                        "New Attribute was created", 
                                        "new attribute was created in one of your projects")
        notification.create_notice_type("context_remove_object", 
                                        "Object was removed", 
                                        "object was removed in one of your projects")
        notification.create_notice_type("context_remove_attribute", 
                                        "Attribute was removed", 
                                        "attribute was removed in one of your projects")
        notification.create_notice_type("intent_changed", 
                                        "Intent of attribute was modified", 
                                        "intent of attribute was modified in one of your projects")
        notification.create_notice_type("attr_imp_conf", 
                                        "New known fact", 
                                        "New known fact")
        notification.create_notice_type("attr_imp_reject", 
                                        "Question was rejected", 
                                        "question was rejected")
        notification.create_notice_type("attr_imp_unconf", 
                                        "Fact became unknown", 
                                        "fact became unknown")
    
    signals.post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"