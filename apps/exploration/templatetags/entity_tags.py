from django.template import Library, Node, TemplateSyntaxError
from django.template import Variable, resolve_variable
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from exploration.models import Entity

register = Library()

def get_contenttype_kwargs(content_object):
    """
    Gets the basic kwargs necessary for form submission url
    """
    kwargs = {
        'content_type_id' : 
            ContentType.objects.get_for_model(content_object).id,
        'object_id' :
            getattr(content_object, 'pk',
                getattr(content_object, 'id')),
    }
    return kwargs
    
def get_entity_form_url(content_object):
    """
    prints url for form action
    """
    kwargs = get_contenttype_kwargs(content_object)
    return reverse('new_entity', kwargs=kwargs)
    
class EntitiesForObjectsNode(Node):
    """
    Get the entities and add to the context
    """
    def __init__(self, obj, context_var):
        self.obj = Variable(obj)
        self.context_var = context_var
        
    def render(self, context):
        content_type = ContentType.objects.get_for_model(
            self.obj.resolve(context)
        )
        # create the template var by adding to context
        context[self.context_var] = \
            Entity.objects.filter( # find all entities for object
                content_type__pk = content_type.id,
                object_id = self.obj.resolve(context).id
            )
        return ''
        
def entities_for_object(parser, token):
    """
    Retrieves a list of entities for given object
    {% entities_for_object foo_object as entity_list %}
    """
    try:
        bits = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError(
            _('tag requires exactly three arguments')
        )
    if len(bits) != 4:
        raise TemplateSyntaxError(
            _('tag requires exactly three arguments')
        )
    if bits[2] != 'as':
        raise TemplateSyntaxError(
            _("second argument to tag must be 'as'")
        )
    return EntitiesForObjectsNode(bits[1], bits[3])
    
def entity_form(parser, token):
    """
    Adds a form to the context as given variable
    {% entity_form as form %}
    """
    # take steps to ensure template var was formatted properly
    try:
        bits = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError(
            _('tag requires exactly two arguments'))
    if bits[1] != 'as':
        raise TemplateSyntaxError(
            _("second argument to tag must be 'as'"))
    if len(bits) != 3:
        raise TemplateSyntaxError(
            _('tag requires exactly two arguments'))
    # get the form
    return EntityFormNode(bits[2])
    
class EntityFormNode(Node):
    """
    Get the form and add it to the context
    """
    def __init__(self, context_name):
        self.context_name = context_name
        
    def render(self, context):
        from exploration.forms import NewEntityForm
        form = NewEntityForm()
        # create the template var by adding to context
        context[self.context_name] = form
        return ''
        
# register these tags for use in template files
register.tag('entities_for_object', entities_for_object)
register.tag('entity_form', entity_form)
register.simple_tag(get_entity_form_url)