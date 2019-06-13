from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.conf import settings
from django.http import JsonResponse, Http404
from django.views import View
from django.views.generic.base import TemplateResponseMixin

import logging
import requests
from requests_saml import HTTPSAMLAuth
from requests_kerberos import HTTPKerberosAuth


logger = logging.getLogger(__name__)


class SendThroughIdP(LoginRequiredMixin, TemplateResponseMixin, View):
    """ allow the user to POST some data; then the render SP's response to it

        data will be exchanged between IdP and SP based on user POST:
            1. user POST to IdP
            2. IdP perform POST to SP
            3. SP perform GET to IdP for more data
            4. IdP return GET request
            5. SP return POST request
            6. user response
    """
    SP_ENDPOINT = '{}/endpoint/'
    template_name = 'endpoint.html'
    extra_context = {
        "known_sp_ids": [x for x in settings.SAML_IDP_SPCONFIG],
    }

    def post(self, request, *args, **kwargs):
        ''' this is where we start data exchange '''
        url = self.SP_ENDPOINT.format('http://localhost:9000')

        user_data = request.POST
        logger.debug(f'received POST from user {request.user!r}')

        # do we have to set cookies?
        cookies = request.COOKIES

        with requests.Session() as session:
            logger.debug('performing requests lib auth config')
            k = HTTPKerberosAuth()
            s = HTTPSAMLAuth(chained_auth=k)

            logger.debug('starting transaction with service provider')
            response = session.post(
                url, data=user_data, cookies=cookies, auth=s)

            logger.debug(f'SP response status: {response.status_code}')

        return self.render_to_response({
            'last_stop': True,
            'sp_response': {
                'header': response.headers,
                'status_code': response.status_code,
                # 'content': str(response.text),
                'content': response.text,
                # 'content': response.content,
            },
        })

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.extra_context)


class ProvideInfo(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        logger.debug('providing data to SP')
        u = request.user
        logger.debug(f'user object: {u}')

        return JsonResponse({
            'username': u.username if u.is_authenticated else 'ANONYMOUS',
            'authenticated': u.is_authenticated,
            # 'META': dict(**request.META),
            # 'headers': str(request.headers),
        })


# Views bellow are related to the alternate protocol:
#   1. user fills a form and POST to service provider
#   2. SP perform POST to IdP for more data
#   3. IdP return POST request
#   4. user response

class PostToSP(LoginRequiredMixin, TemplateResponseMixin, View):
    ''' allow user to POST directly to service provider '''
    SP_ENDPOINT = '{}/endpoint/direct/'
    template_name = 'send_to_sp.html'
    extra_context = {
        "known_sp_ids": [x for x in settings.SAML_IDP_SPCONFIG],
        "sp_url": SP_ENDPOINT.format('http://localhost:9000'),
    }

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.extra_context)


class AlternateProvideInfo(LoginRequiredMixin, View):
    """ provide some info based on correct data

        example: provide user's last login date if POST data
            (username, date_joined) are correct
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        ''' will provide JSON data if POST parameters exist in DB '''
        data = request.POST
        print(data)
        try:
            user = User.objects.get(username=data.get('username'))
        except User.DoesNotExist:
            raise Http404

        return JsonResponse({
            'id': user.pk,
            'last_login': user.last_login,
            'date_joined': user.date_joined,
            'is_authenticated': user.is_authenticated,
        })
