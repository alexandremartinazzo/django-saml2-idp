from django.urls import include, path
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt

from idp.views import (
    SendThroughIdP, ProvideInfo,
    PostToSP, AlternateProvideInfo
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('idp/', include('djangosaml2idp.urls')),
    path('', TemplateView.as_view(template_name="index.html")),
    path('iframe/', TemplateView.as_view(template_name="iframe.html")),

    # Transactional protocol: user POST to IDP which will perform data exchange
    path('endpoint/post/', SendThroughIdP.as_view(), name='endpoint_post'),
    path('endpoint/get/', ProvideInfo.as_view(), name='endpoint_get'),

    # Alternate transactional protocol: user POST to SP, which will retrieve
    # data from IdP
    path('endpoint/direct/',
         PostToSP.as_view(),
         name='endpoint_direct'),
    path('endpoint/alternate_get/',
         # csrf_exempt(AlternateProvideInfo.as_view()),
         AlternateProvideInfo.as_view(),
         name='endpoint_alternate_get'),
]
