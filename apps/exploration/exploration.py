#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tempfile
import os
import subprocess
from sail.settings import MEDIA_ROOT

import fca
from fca.readwrite import uwrite_dot
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
        self._data = {}
        self._counter = 0

    def __getitem__(self, key):
        return self._data[key]
    
    def __iter__(self):
        for imp in self._data.values():
            yield imp

    def _get_implications(self):
        return self._data

    def append(self, fca_imp):
        fca_imp.pk = self._counter
        self._data[self._counter] = fca_imp
        self._counter += 1

    def get_query_set(self, attributes):
        for imp in self:
            yield TranslatedImplication(imp, attributes)

    def remove(self, imp):
        pass

    def update(self, imp_list):
        self._data = {}
        
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

    def _get_self_as_fca_context(self, pk=True):
        objects = self.group.content_objects(FObject)
        attributes = self.group.content_objects(FAttribute)
        if pk:
            object_names = [obj.pk for obj in objects]
            attribute_names = [attr.pk for attr in attributes]
        else:
            object_names = [obj.name for obj in objects]
            attribute_names = [attr.name for attr in attributes]
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

    def add_object_with_intent(self, intent, name):
        obj = FObject(name=name, group=self.group)
        obj.save()
        if len(intent) != 0:
            get_attr = lambda name: self.group.content_objects(FAttribute).get(pk=name)
            obj.attributes.add(*[get_attr(pk) for pk in intent])

    def add_attribute_with_extent(self, extent, name):
        attr = FObject(name=name, group=self.group)
        attr.save()
        if len(extent) != 0:
            get_obj = lambda name: self.group.content_objects(FObject).get(pk=name)
            attr.fobject_set.add(*[get_obj(pk) for pk in extent])

class WebExpert(object):

    def set_counterexample(self, example, intent):
        self.example = example
        self.intent = intent

    def provide_counterexample(self, imp):
        return (self.example, self.intent)

class WebExploration(AttributeExploration):

    def __init__(self, group):
        db = ExplorationDB(DBContext(group), BackgroundKnowledgeList(group))
        expert = WebExpert()
        super(WebExploration, self).__init__(db, expert)

    def confirm_implication(self, imp_pk):
        imp = self.db.open_implications[imp_pk]
        super(WebExploration, self).confirm_implication(imp)
        return imp

    def unconfirm_implication(self, imp_pk):
        super(WebExploration, self).unconfirm_implication(AttributeImplication.objects.get(pk=imp_pk))

    def reject_implication(self, imp_pk):
        imp = self.db.open_implications[imp_pk]
        super(WebExploration, self).reject_implication(imp)

class ExplorationWrapper(object):

    _explorations = {}

    @classmethod
    def save_lattice(cls, group):
        temp_dot_path = tempfile.mktemp()
        dir_path = os.path.join(MEDIA_ROOT, "img", group.slug)
        
        cxt = cls._explorations[group].db._cxt._get_self_as_fca_context(pk=False)

        concept_system = fca.ConceptLattice(cxt)
        uwrite_dot(concept_system, temp_dot_path, full=True)
        
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        svg_path = os.path.join(dir_path, "lattice.svg")
        try:
            subprocess.call(["dot", "-Tsvg", 
                            "-o{0}".format(svg_path),
                            temp_dot_path])
        except:
            # TODO: workaround for windows systems
            pass

    @classmethod
    def clear(cls):
        cls._explorations.clear()

    @classmethod
    def get_exploration(cls, group):
        if group not in cls._explorations:
            cls._explorations[group] = WebExploration(group)
        return cls._explorations[group]

    @classmethod
    def get_open_implications(cls, group):
        # To find relative basis (open implications) we treat attributes as
        # primary keys of corresponding attributes in database. Therefore we
        # need to translate them to readable format.
        attributes = {attr.pk : attr.name for attr in group.content_objects(FAttribute)}
        # open_implications is object of class ImplicationsList (also defined
        # in this module)
        return cls.get_exploration(group).db.open_implications.get_query_set(attributes)

    @classmethod
    def confirm_implication(cls, group, imp_pk):
        return cls.get_exploration(group).confirm_implication(imp_pk)

    @classmethod
    def get_premise(cls, group, imp_pk):
        return cls.get_exploration(group).db.open_implications[imp_pk].premise

    @classmethod
    def get_conclusion(cls, group, imp_pk):
        return cls.get_exploration(group).db.open_implications[imp_pk].conclusion

    @classmethod
    def unconfirm_implication(cls, group, imp_pk):
        cls.get_exploration(group).unconfirm_implication(imp_pk)

    @classmethod
    def reject_implication_with_counterexample(cls, group, imp_pk, example, intent):
        cls.get_exploration(group).expert.set_counterexample(example, intent)
        cls.get_exploration(group).reject_implication(imp_pk)
        cls.save_lattice(group)

    @classmethod
    def get_background_knowledge(cls, group):
        return cls.get_exploration(group).db.base.get_query_set()

    @classmethod
    def edit_object(cls, group, object_, intent):
        cls.get_exploration(group).db.edit_example(object_, object_, intent)
        cls.save_lattice(group)

    @classmethod
    def add_attribute(cls, group, attribute, extent):
        cls.get_exploration(group).db.add_attribute(attribute, extent)
        cls.save_lattice(group)

    @classmethod
    def touch(cls, group):
        cls.get_exploration(group).db.touch()
        cls.save_lattice(group)