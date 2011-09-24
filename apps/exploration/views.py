from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django import forms
from django.utils import simplejson

import urllib

from models import FObject, FAttribute
from misc import import_context, prepare_data_for_edit

def group_context(group, bridge):
    # @@@ use bridge
    ctx = {
        "group": group,
    }
    if group:
        ctx["group_base"] = bridge.group_base_template()
    return ctx

def group_and_bridge(request):
    """
    Given the request we can depend on the GroupMiddleware to provide the
    group and bridge.
    """
    
    # be group aware
    group = getattr(request, "group", None)
    if group:
        bridge = request.bridge
    else:
        bridge = None
    
    return group, bridge

@login_required    
def knowledge_base(request, template_name="exploration/kb.html"):
    """Displays objects and attributes
    """
    group, bridge = group_and_bridge(request)
    ctx = group_context(group, bridge)
    
    filter_list = request.GET.getlist("a")
    now_filtering = len(filter_list) != 0
    filter_list = [urllib.unquote(attr) for attr in filter_list]
    if now_filtering:
        objects = []
        attributes_set = set()
        for obj in group.content_objects(FObject):
            if obj.has_attributes(filter_list):
                objects.append(obj)
                attributes_set = attributes_set | set(obj.attributes.all())
        attributes = list(attributes_set)
    else:
        objects = group.content_objects(FObject)
        attributes = group.content_objects(FAttribute)
    data_dictionary = {
        "objects" : objects,
        "attributes" : attributes,
        "filtering" : now_filtering,
        "current_path" : request.get_full_path(),
        "filter_list" : filter_list,
        "project": group,
    }
    return render_to_response(template_name, 
                              data_dictionary, 
                              context_instance=RequestContext(request, ctx))

class UploadFileForm(forms.Form):
    import_context = forms.FileField()
                              
@login_required                              
def import_context_view(request, template_name="exploration/import.html"):
    """docstring for import_context"""
    group, bridge = group_and_bridge(request)
    ctx = group_context(group, bridge)
    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            if request.user.is_authenticated():
                import_context(group, request.FILES['import_context'])
            else:
                # TODO: Show message
                pass
            return HttpResponseRedirect(bridge.reverse('knowledge_base_index', group))
    else:
        form = UploadFileForm()
    return render_to_response(template_name,
                            { "form" : form },
                            context_instance=RequestContext(request, ctx))

@login_required
def object_details(request, id, template_name="exploration/objects/details.html"):
    group, bridge = group_and_bridge(request)
    ctx = group_context(group, bridge)
    
    object_ = get_object_or_404(FObject, pk=id)
    data_dictionary = {
        "object" : object_,
        "project": group,
    }
    return render_to_response(template_name,
                              data_dictionary,
                              context_instance=RequestContext(request, ctx))
@login_required                       
def edit_knowledge_base(request, template_name="exploration/edit.html"):
    """Edit knowledge base view"""
    group, bridge = group_and_bridge(request)
    ctx = group_context(group, bridge)
    
    context, objects, attributes = prepare_data_for_edit(group)
    data_dictionary = {
        "objects" : objects,
        "attributes" : attributes,
    }
    return render_to_response(template_name, 
                              data_dictionary, 
                              context_instance=RequestContext(request, ctx))
                              
                              
@login_required
def get_intent(request):
    """AJAX"""
    if request.method == 'POST':
        pk = request.POST['pk']
        object = FObject.objects.get(pk=pk)
        attributes = object.attributes.all()
        attributes_ids = [attr.pk for attr in attributes]
        return HttpResponse(simplejson.dumps(attributes_ids, ensure_ascii=False), 
                                mimetype='application/json')
    else:
        raise Http404

@login_required
def submit_intent(request):
    """AJAX"""
    if request.method == 'POST':
        pk = request.POST['pk']
        object = FObject.objects.get(pk=pk)
        intent = [int(id_) for id_ in request.POST.getlist(u'intent[]')]
        object.set_intent(intent)
        status = 'ok'
        return HttpResponse(simplejson.dumps({'status' : status}, ensure_ascii=False), 
                            mimetype='application/json')
    else:
        raise Http404