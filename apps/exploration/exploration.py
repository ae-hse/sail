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
        return self.group.content_objects(AttributeImplication).filter(is_confirmed=True)

    def append(self, imp):
        implications_objects = super(BackgroundKnowledgeList, self)._get_implications()
        imp_obj = implications_objects.get(pk=imp.pk)
        imp_obj.is_confirmed = True
        imp_obj.save()


class ImplicationsList(ImplicationsContainer):
    """Interface for list of open implications (relative basis)"""
    
    def _get_implications(self):
        return self.group.content_objects(AttributeImplication).filter(is_confirmed=False)

    def append(self, fca_imp):
        db_imp = AttributeImplication(is_confirmed=False)
        self.group.associate(db_imp, commit=False)
        db_imp.save()
        for name in fca_imp.get_premise():
            db_imp.premise.add(self.group.content_objects(FAttribute).get(pk=name))
        for name in fca_imp.get_conclusion() - fca_imp.get_premise():
            db_imp.conclusion.add(self.group.content_objects(FAttribute).get(pk=name))

    def update(self, imp_list):
        for imp in self:
            if imp not in imp_list:
                self.remove(imp)

        for imp in imp_list:
            if imp not in self:
                self.append(imp)


class DBContext(fca.Context):
    """Facade for web-site db emulating context

    Works with objects' and attributes' pks, not names
    """
    def __init__(self, group):
        super(DBContext, self).__init__()
        self.group = group

        self._implications = ImplicationsList(group)

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

    def get_open_implications(self):
        return self.exploration.get_open_implications()

    def get_background_knowledge(self):
        return self.db.base

    def confirm_implication(self, imp_pk):
        self.exploration.confirm_implication(AttributeImplication.objects.get(pk=imp_pk))


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
        return cls.get_expert(group).get_open_implications().get_query_set()

    @classmethod
    def confirm_implication(cls, group, imp_pk):
        cls.get_expert(group).confirm_implication(imp_pk)

    @classmethod
    def get_background_knowledge(cls, group):
        return cls.get_expert(group).get_background_knowledge().get_query_set()

    @classmethod
    def edit_object(cls, group, object_, intent):
        cls.get_expert(group).db.edit_example(object_, object_, intent)