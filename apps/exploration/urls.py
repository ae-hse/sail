from django.conf.urls.defaults import *

urlpatterns = patterns("",
    url(r"^$", "exploration.views.knowledge_base", name="knowledge_base_index"),
)