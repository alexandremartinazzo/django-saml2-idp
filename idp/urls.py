from django.urls import include, path
from django.contrib import admin
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('idp/', include('djangosaml2idp.urls')),
    path('', TemplateView.as_view(template_name="index.html")),
    path('iframe/', TemplateView.as_view(template_name="iframe.html")),
]
