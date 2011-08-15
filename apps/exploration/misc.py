from models import FObject, FAttribute

import fca

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
        for attribute_name in cxt.attributes:
            if attribute_name in object_intent:
                obj.attributes.add(group.content_objects(FAttribute).get(name=attribute_name))
                
def clear_db(group):
    group.content_objects(FObject).delete()
    group.content_objects(FAttribute).delete()