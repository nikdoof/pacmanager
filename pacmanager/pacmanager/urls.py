from django.core.urlresolvers import reverse_lazy
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView

admin.autodiscover()

urlpatterns = patterns('',

    # Base
    url(r'^$', RedirectView.as_view(url=reverse_lazy('corporation-list'))),
    url(r'', include('core.urls')),
    url(r'', include('django.contrib.auth.urls')),

    # Admin
    url(r'^admin/', include(admin.site.urls)),
)
