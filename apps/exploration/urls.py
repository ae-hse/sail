from django.conf.urls.defaults import *

urlpatterns = patterns("",
	# Knowledge base urls
    url(r"^$", "exploration.views.knowledge_base", name="knowledge_base_index"),
    url(r"^import$", "exploration.views.import_context_view", name="import_context"),
    url(r"^edit$", "exploration.views.edit_knowledge_base", name="edit_kb"),
    url(r"^implications$", "exploration.views.implications", name="implications"),
    # Objects' urls
    url(r"^object/new/$", "exploration.views.object_new", name="object_new"),
    url(r"^object/(?P<id>\d+)/$", "exploration.views.object_details", name="object_details"),
    url(r"^object/(?P<id>\d+)/edit/$", "exploration.views.object_edit", name="object_edit"),
    # Attributes' urls
    url(r"^attribute/new/$", "exploration.views.attribute_new", name="attribute_new"),
    # AJAX
    url(r"^getintent$", "exploration.views.get_intent", name="get_intent"),
    url(r"^submitintent$", "exploration.views.submit_intent", name="submit_intent"),
    url(r"^confirmimplication$", "exploration.views.confirm_implication", name="confirm_implication"),
)