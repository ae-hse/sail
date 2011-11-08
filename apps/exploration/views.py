from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils import simplejson
from django.db import transaction

import urllib
import datetime

from forms import ObjectForm, AttributeForm
from models import FObject, FAttribute
from misc import import_context, prepare_data_for_edit, get_csv
from exploration import ExplorationWrapper

# Uncomment next line if you want to use profiler
# from utils.profiler import profile

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

    is_member = group.user_is_member(request.user)

    if not is_member:
        return HttpResponseForbidden("You must be a project member to do this")
    
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
@transaction.commit_manually
def import_context_view(request, template_name="exploration/import.html"):
    """docstring for import_context"""
    group, bridge = group_and_bridge(request)
    ctx = group_context(group, bridge)

    is_member = group.user_is_member(request.user)

    if not is_member:
        return HttpResponseForbidden("You must be a project member to do this")
    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            if request.user.is_authenticated():
                import_context(group, request.FILES['import_context'])
                transaction.commit()
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

    is_member = group.user_is_member(request.user)

    if not is_member:
        return HttpResponseForbidden("You must be a project member to do this")
    
    object_ = get_object_or_404(FObject, pk=id)
    data_dictionary = {
        "object" : object_,
        "project": group,
    }
    return render_to_response(template_name,
                              data_dictionary,
                              context_instance=RequestContext(request, ctx))

@login_required
def object_new(request, template_name="exploration/objects/new.html"):
    group, bridge = group_and_bridge(request)
    ctx = group_context(group, bridge)

    is_member = group.user_is_member(request.user)

    if not is_member:
        return HttpResponseForbidden("You must be a project member to do this")

    if request.method == 'POST':
        form = ObjectForm(request.POST)
        if form.is_valid():
            object_ = form.save(commit=False)
            if group:
                group.associate(object_, commit=False)
            object_.save()
            ExplorationWrapper.touch(group)
            return HttpResponseRedirect(bridge.reverse('object_details', group, {"id" : object_.id}))
        else:
            # TODO: Possibly validation error handling
            return HttpResponseRedirect(bridge.reverse('knowledge_base_index', group))
    else:
        form = ObjectForm()

    data_dictionary = {
        "project": group,
        "form" : form
    }

    return render_to_response(template_name,
                              data_dictionary,
                              context_instance=RequestContext(request, ctx))

@login_required
def attribute_new(request, template_name="exploration/attributes/new.html"):
    group, bridge = group_and_bridge(request)
    ctx = group_context(group, bridge)

    is_member = group.user_is_member(request.user)

    if not is_member:
        return HttpResponseForbidden("You must be a project member to do this")

    if request.method == 'POST':
        form = AttributeForm(request.POST)
        if form.is_valid():
            attribute = form.save(commit=False)
            if group:
                group.associate(attribute, commit=False)
            attribute.save()
            ExplorationWrapper.touch(group)
        return HttpResponseRedirect(bridge.reverse('knowledge_base_index', group))
    else:
        form = AttributeForm()

    data_dictionary = {
        "project": group,
        "form" : form
    }

    return render_to_response(template_name,
                              data_dictionary,
                              context_instance=RequestContext(request, ctx))

@login_required
def object_edit(request, id, template_name="exploration/objects/edit.html"):
    group, bridge = group_and_bridge(request)
    ctx = group_context(group, bridge)

    is_member = group.user_is_member(request.user)

    if not is_member:
        return HttpResponseForbidden("You must be a project member to do this")
    
    object_ = get_object_or_404(FObject, pk=id)
    if request.method == 'POST':
        if 'delete' in request.POST:
            object_.delete()
            ExplorationWrapper.touch(group)
            return HttpResponseRedirect(bridge.reverse('edit_kb', group))
        else:
            form = ObjectForm(request.POST, instance=object_)
            if form.is_valid():
                form.save()
                ExplorationWrapper.touch(group)
            return HttpResponseRedirect(bridge.reverse('object_details', group, {"id" : object_.id}))
    else:
        form = ObjectForm(instance=object_)
    
    data_dictionary = {
        "object" : object_,
        "project": group,
        "form" : form
    }
    return render_to_response(template_name,
                              data_dictionary,
                              context_instance=RequestContext(request, ctx))

def attribute_edit(request, id, template_name="exploration/attributes/edit.html"):
    group, bridge = group_and_bridge(request)
    ctx = group_context(group, bridge)

    is_member = group.user_is_member(request.user)

    if not is_member:
        return HttpResponseForbidden("You must be a project member to do this")
    
    attr = get_object_or_404(FAttribute, pk=id)
    if request.method == 'POST':
        if 'delete' in request.POST:
            attr.delete()
            ExplorationWrapper.touch(group)
            return HttpResponseRedirect(bridge.reverse('edit_attributes', group))
        else:
            form = AttributeForm(request.POST, instance=attr)
            if form.is_valid():
                form.save()
                ExplorationWrapper.touch(group)
            return HttpResponseRedirect(bridge.reverse('edit_attributes', group,))
    else:
        form = AttributeForm(instance=attr)
    
    data_dictionary = {
        "attribute" : attr,
        "project": group,
        "form" : form
    }
    return render_to_response(template_name,
                              data_dictionary,
                              context_instance=RequestContext(request, ctx))

@login_required                       
def edit_knowledge_base(request, template_name="exploration/edit.html"):
    """Edit knowledge base view"""
    group, bridge = group_and_bridge(request)
    ctx = group_context(group, bridge)

    is_member = group.user_is_member(request.user)

    if not is_member:
        return HttpResponseForbidden("You must be a project member to do this")
    
    objects, attributes = prepare_data_for_edit(group)
    data_dictionary = {
        "objects" : objects,
        "attributes" : attributes,
        "project" : group,
    }
    return render_to_response(template_name, 
                              data_dictionary, 
                              context_instance=RequestContext(request, ctx))


@login_required                       
def edit_attributes(request, template_name="exploration/attributes.html"):
    """Edit knowledge base view"""
    group, bridge = group_and_bridge(request)
    ctx = group_context(group, bridge)

    is_member = group.user_is_member(request.user)

    if not is_member:
        return HttpResponseForbidden("You must be a project member to do this")
    
    objects, attributes = prepare_data_for_edit(group)
    data_dictionary = {
        "objects" : objects,
        "attributes" : attributes,
        "project" : group,
    }
    return render_to_response(template_name, 
                              data_dictionary, 
                              context_instance=RequestContext(request, ctx))

@login_required
def implications(request, template_name="exploration/implications.html"):
    group, bridge = group_and_bridge(request)
    ctx = group_context(group, bridge)

    is_member = group.user_is_member(request.user)

    if not is_member:
        return HttpResponseForbidden("You must be a project member to do this")

    open_implications = ExplorationWrapper.get_open_implications(group)
    # open_implications = [open_implications_generator.next() for _ in xrange(10)]
    confirmed_implications = ExplorationWrapper.get_background_knowledge(group)
    attributes = group.content_objects(FAttribute)

    data_dictionary = {
        "project" : group,
        "open_implications" : open_implications,
        "confirmed_implications" : confirmed_implications,
        "attributes" : attributes,
    }
    return render_to_response(template_name, 
                              data_dictionary, 
                              context_instance=RequestContext(request, ctx))
                              
@login_required
def get_intent(request):
    """AJAX"""
    group, bridge = group_and_bridge(request)

    is_member = group.user_is_member(request.user)

    if not is_member:
        return HttpResponseForbidden("You must be a project member to do this")

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
def get_premise(request):
    """AJAX"""
    group, bridge = group_and_bridge(request)

    is_member = group.user_is_member(request.user)

    if not is_member:
        return HttpResponseForbidden("You must be a project member to do this")

    if request.method == 'POST':
        imp_pk = request.POST['imp_pk']
        try:
            attributes_ids = ExplorationWrapper.get_premise(group, int(imp_pk))
        except:
            return HttpResponse("reload")

        return HttpResponse(simplejson.dumps(list(attributes_ids), ensure_ascii=False), mimetype='application/json')
    else:
        raise Http404

@login_required
def get_conclusion(request):
    """AJAX"""
    group, bridge = group_and_bridge(request)

    is_member = group.user_is_member(request.user)

    if not is_member:
        return HttpResponseForbidden("You must be a project member to do this")

    if request.method == 'POST':
        imp_pk = request.POST['imp_pk']
        try:
            attributes_ids = ExplorationWrapper.get_conclusion(group, int(imp_pk))
        except:
            return HttpResponse("reload")

        return HttpResponse(simplejson.dumps(list(attributes_ids), ensure_ascii=False), mimetype='application/json')
    else:
        raise Http404

@login_required
def submit_intent(request):
    """AJAX"""
    group, bridge = group_and_bridge(request)

    is_member = group.user_is_member(request.user)

    if not is_member:
        return HttpResponseForbidden("You must be a project member to do this")

    if request.method == 'POST':
        object_pk = int(request.POST['pk'])
        intent = [int(id_) for id_ in request.POST.getlist(u'intent[]')]
        try:
            ExplorationWrapper.edit_object(group, object_pk, set(intent))
            status = 'ok'
        except Exception as details:
            status = str(details)
        return HttpResponse(simplejson.dumps({'status' : status}, ensure_ascii=False), 
                            mimetype='application/json')
    else:
        raise Http404

@login_required
def confirm_implication(request):
    """AJAX"""
    group, bridge = group_and_bridge(request)

    is_member = group.user_is_member(request.user)

    if not is_member:
        return HttpResponseForbidden("You must be a project member to do this")

    if request.method == 'POST':
        pk = request.POST['pk']
        try:
            ExplorationWrapper.confirm_implication(group, int(pk))
        except KeyError:
            # TODO: Relative basis was changed. Show message.
            pass
        return HttpResponseRedirect(bridge.reverse('implications', group))
    else:
        raise Http404

@login_required
def unconfirm_implication(request):
    group, bridge = group_and_bridge(request)

    is_member = group.user_is_member(request.user)

    if not is_member:
        return HttpResponseForbidden("You must be a project member to do this")

    if request.method == 'POST':
        pk = request.POST['pk']
        ExplorationWrapper.unconfirm_implication(group, pk)
        return HttpResponseRedirect(bridge.reverse('implications', group))
    else:
        raise Http404

@login_required
def reject_implication(request):
    group, bridge = group_and_bridge(request)

    is_member = group.user_is_member(request.user)

    if not is_member:
        return HttpResponseForbidden("You must be a project member to do this")

    if request.method == 'POST':
        try:
            object_name = request.POST['example_name']
            if len(object_name) == 0:
                raise Exception("Object's name can't be empty")
            imp_pk = int(request.POST['imp_pk'])
            intent = set()
            for key in request.POST:
                if key != 'example_name' and key != 'imp_pk':
                    intent.add(int(key))
            premise = ExplorationWrapper.get_premise(group, int(imp_pk))
            ExplorationWrapper.reject_implication_with_counterexample(group, imp_pk, object_name, premise | intent)
            status = 'ok'
        except Exception as details:
            status = str(details)
        return HttpResponse(simplejson.dumps({'status' : status}, ensure_ascii=False), 
                            mimetype='application/json')
    else:
        raise Http404

@login_required
def export_context(request):
    group, bridge = group_and_bridge(request)

    is_member = group.user_is_member(request.user)

    if not is_member:
        return HttpResponseForbidden("You must be a project member to do this")

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename=context-{0}.csv'.format(datetime.date.today())
    response.write(get_csv(group))
    
    return response