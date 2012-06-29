from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns("",
    url(r"^$", direct_to_template, {"template": "about/about.html"}, name="about"),
    url(r"^terms/$", direct_to_template, {"template": "about/terms.html"}, name="terms"),
    url(r"^privacy/$", direct_to_template, {"template": "about/privacy.html"}, name="privacy"),
    url(r"^dmca/$", direct_to_template, {"template": "about/dmca.html"}, name="dmca"),
    url(r"^what_next/$", direct_to_template, {"template": "about/what_next.html"}, name="what_next"),
    url(r"^tutor_contents/$", direct_to_template, {"template": "about/tutor/tutor_contents.html"}, name="tutor_contents"),
    url(r"^tutor_crt_project/$", direct_to_template, {"template": "about/tutor/tutor_create_project.html"}, name="tutor_create_project"),
    url(r"^tutor_main_page/$", direct_to_template, {"template": "about/tutor/tutor_main_page.html"}, name="tutor_main_page"),
    url(r"^tutor_knowledge_base/$", direct_to_template, {"template": "about/tutor/tutor_knowledge_base.html"}, name="tutor_knowledge_base"),
    url(r"^tutor_filling_base/$", direct_to_template, {"template": "about/tutor/tutor_filling_base.html"}, name="tutor_filling_base"),
    url(r"^tutor_link_objects/$", direct_to_template, {"template": "about/tutor/tutor_link_objects.html"}, name="tutor_link_objects"),
    url(r"^tutor_lattice/$", direct_to_template, {"template": "about/tutor/tutor_lattice.html"}, name="tutor_lattice"),
    url(r"^tutor_questions/$", direct_to_template, {"template": "about/tutor/tutor_questions.html"}, name="tutor_questions"),
    url(r"^test/$", direct_to_template, {"template": "about/test.html"}, name="test"),
)
