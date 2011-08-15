from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

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
    """Displays knowledge base management tools
    """
    group, bridge = group_and_bridge(request)
    
    ctx = group_context(group, bridge)
    
    return render_to_response(template_name, RequestContext(request, ctx))
