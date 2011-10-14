#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fca
from fca.algorithms.exploration.exploration import (AttributeExploration, 
                                                    ExplorationDB)

from models import FObject, FAttribute, AttributeImplication

class ImplicationsContainer(object):

    def __init__(self, group):
        self.group = group

    def __iter__(self):
        for imp in self._get_implications():
            fca_imp = fca.Implication(imp.get_premise(), imp.get_conclusion())
            # !!!
            fca_imp.pk = imp.pk
            yield fca_imp

    def _get_implications(self):
        return self.group.content_objects(AttributeImplication)

    def get_query_set(self):
        return self._get_implications()

    def get_as_plain_list(self):
        return list(self)

    def remove(self, imp):
        implications_objects = self._get_implications()
        imp_obj = implications_objects.get(pk=imp.pk)
        imp_obj.delete()

class BackgroundKnowledgeList(ImplicationsContainer):
    """Interface for background knowledge implications"""
    
    def _get_implications(self):
        return self.group.content_objects(AttributeImplication)

    def append(self, fca_imp):
        db_imp = AttributeImplication()
        self.group.associate(db_imp, commit=False)
        db_imp.save()

        get_attr = lambda name: self.group.content_objects(FAttribute).get(pk=name)
        db_imp.premise.add(*[get_attr(name) for name in fca_imp.premise])
        db_imp.conclusion.add(*[get_attr(name) for name in fca_imp.conclusion])

class TranslatedImplication(fca.Implication):

    def __init__(self, fca_imp, attributes):
        self._premise = set([attributes[pk] for pk in fca_imp.premise])
        self._conclusion = set([attributes[pk] for pk in fca_imp.conclusion])
        self.pk = fca_imp.pk

class ImplicationsList(object):
    """Interface for list of open implications (relative basis)"""

    def __init__(self):
        self._data = []

    def __getitem__(self, key):
        return self._data[key]
    
    def __iter__(self):
        for imp in self._data:
            yield imp

    def _get_implications(self):
        return self._data

    def append(self, fca_imp):
        fca_imp.pk = len(self._data)
        self._data.append(fca_imp)

    def get_query_set(self, attributes):
        for imp in self:
            yield TranslatedImplication(imp, attributes)

    def remove(self, imp):
        pass

    def update(self, imp_list):
        self._data = []
        
        for imp in imp_list:
            self.append(imp)


class DBContext(fca.Context):
    """Facade for web-site db emulating context

    Works with objects' and attributes' pks, not names
    """
    def __init__(self, group):
        super(DBContext, self).__init__()
        self.group = group

        self._implications = ImplicationsList()

    def _get_self_as_fca_context(self):
        objects = self.group.content_objects(FObject)
        attributes = self.group.content_objects(FAttribute)
        object_names = [obj.pk for obj in objects]
        attribute_names = [attr.pk for attr in attributes]
        table = []
        for obj in objects:
            table.append(obj.get_as_boolean_list(self.group))
        return fca.Context(table, object_names, attribute_names)

    def get_objects(self):
        objects = self.group.content_objects(FObject)
        return [obj.pk for obj in objects]

    objects = property(get_objects)

    def get_attribute_implications(self, 
                                   basis=fca.algorithms.compute_dg_basis,
                                   confirmed=[],
                                   cond=lambda x: True):
        imp_basis = confirmed.get_as_plain_list()
        rel_basis = basis(self._get_self_as_fca_context(), imp_basis=imp_basis, cond=cond)
        self._implications.update(rel_basis)
        return self._implications

    def set_object_intent(self, intent, name):
        obj = self.group.content_objects(FObject).get(pk=name)
        obj.attributes.clear()
        for attr in intent:
            obj.attributes.add(self.group.content_objects(FAttribute).get(pk=attr))

    def get_object_intent(self, name):
        obj = self.group.content_objects(FObject).get(pk=name)
        return set([attr.pk for attr in obj.attributes.all()])



class WebExpert(object):

    def __init__(self, group):
        self.db = ExplorationDB(DBContext(group), BackgroundKnowledgeList(group))
        self.exploration = AttributeExploration(self.db, self)
        self._last_implications = []

    def get_open_implications(self):
        self._last_implications = self.exploration.get_open_implications()
        return self._last_implications

    def get_background_knowledge(self):
        return self.db.base

    def confirm_implication(self, imp_pk):
        # TODO: Potentially it may lead to undetermined behaviour.
        # What if _last_implications was changed since last time?
        # May be we should somehow block implication page while exploration
        self.exploration.confirm_implication(self._last_implications[imp_pk])

    def unconfirm_implication(self, imp_pk):
        self.exploration.unconfirm_implication(AttributeImplication.objects.get(pk=imp_pk))

class ExplorationWrapper(object):

    _experts = {}

    @classmethod
    def clear_experts(cls):
        cls._experts.clear()

    @classmethod
    def get_expert(cls, group):
        if group not in cls._experts:
            cls._experts[group] = WebExpert(group)
        return cls._experts[group]

    @classmethod
    def get_open_implications(cls, group):
        attributes = {attr.pk : attr.name for attr in group.content_objects(FAttribute)}
        return cls.get_expert(group).get_open_implications().get_query_set(attributes)

    @classmethod
    def confirm_implication(cls, group, imp_pk):
        cls.get_expert(group).confirm_implication(imp_pk)

    @classmethod
    def unconfirm_implication(cls, group, imp_pk):
        cls.get_expert(group).unconfirm_implication(imp_pk)

    @classmethod
    def get_background_knowledge(cls, group):
        return cls.get_expert(group).get_background_knowledge().get_query_set()

    @classmethod
    def edit_object(cls, group, object_, intent):
        cls.get_expert(group).db.edit_example(object_, object_, intent)