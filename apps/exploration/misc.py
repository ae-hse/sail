from models import FObject, FAttribute, AttributeImplication
from exploration import ExplorationWrapper

from StringIO import StringIO

import fca

def prepare_data_for_edit(group):
    """Prepares data for knowledge base edit view"""
    objects = group.content_objects(FObject)
    attributes = group.content_objects(FAttribute)

    return objects, attributes

def import_context(group, file_):
    """Read context from uploaded cxt file and replace current context with it
    """
    input_file = file_
    assert input_file.readline().strip() == "B",\
        "File is not valid cxt"
    input_file.readline() # Empty line
    number_of_objects = int(input_file.readline().strip())
    number_of_attributes = int(input_file.readline().strip())
    input_file.readline() # Empty line

    objects = [input_file.readline().strip() 
               for i in xrange(number_of_objects)]
    attributes = [input_file.readline().strip() 
                  for i in xrange(number_of_attributes)]

    table = []
    for i in xrange(number_of_objects):
        line = map(lambda c: c=="X", input_file.readline().strip())
        table.append(line)

    input_file.close()

    cxt = fca.Context(table, objects, attributes)
    set_context(group, cxt)
    
def set_context(group, cxt):
    """Set current context to context from fca.context"""
    clear_db(group)
    for attribute_name in cxt.attributes:
        attr = FAttribute(name=attribute_name, group=group)
        attr.save()

    for object_name in cxt.objects:
        obj = FObject(name=object_name, group=group)
        obj.save()
        object_intent = cxt.get_object_intent(object_name)
        get_attr = lambda name: group.content_objects(FAttribute).get(name=name)
        obj.attributes.add(*[get_attr(name) for name in object_intent])
                
def clear_db(group):
    group.content_objects(FObject).delete()
    group.content_objects(FAttribute).delete()
    group.content_objects(AttributeImplication).delete()
    ExplorationWrapper.clear()

def get_csv(group):
    all_objects = group.content_objects(FObject)
    all_attributes = group.content_objects(FAttribute)
    object_names = [obj.name for obj in all_objects]
    attribute_names = [attr.name for attr in all_attributes]
    table = []
    for obj in all_objects:
        table.append(obj.get_as_boolean_list(group))
    
    out = StringIO()
    q = lambda s: s.replace('\"', '\'')
    print >>out, u";" + u";".join(q(attr) for attr in attribute_names)
    f = lambda n: u"1" if n else u"0"
    for i in xrange(len(object_names)):
        print >>out, u";".join([q(object_names[i])] + [f(n) for n in table[i]])
    return out.getvalue()