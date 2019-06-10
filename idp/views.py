from django.conf import settings
from django.views.generic import TemplateView


class EndPoint(TemplateView):
    template_name = 'endpoint.html'
    extra_context = {
        "known_sp_ids": [x for x in settings.SAML_IDP_SPCONFIG],
    }
