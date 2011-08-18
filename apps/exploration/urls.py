from django.conf.urls.defaults import *

urlpatterns = patterns("",
    url(r"^$", "exploration.views.knowledge_base", name="knowledge_base_index"),
    url(r"^import$", "exploration.views.import_context_view", name="import_context"),
    url(r"^object/(?P<id>\d+)/$", "exploration.views.object_details", name="object_details"),
    url(r"^edit$", "exploration.views.edit_knowledge_base", name="edit_kb"),
    url(r"^getintent$", "exploration.views.get_intent", name="get_intent"),
)