from django.conf.urls import patterns, include, url
from .views import CorporationListView, CorporationDetailView, CorporationUpdateContactView, ManualAdjustmentView, KeyCreateView, KeyListView, KeyDeleteView, KeyRefreshView, KeyImportView, ChargeTotalView

urlpatterns = patterns('',

    url(r'^keys/$', KeyListView.as_view(), name='key-list'),
    url(r'^keys/new/$', KeyCreateView.as_view(), name='key-create'),
    url(r'^keys/(?P<pk>\d+)/delete/$', KeyDeleteView.as_view(), name='key-delete'),
    url(r'^keys/(?P<pk>\d+)/refresh/$', KeyRefreshView.as_view(), name='key-refresh'),
    url(r'^keys/(?P<pk>\d+)/import/$', KeyImportView.as_view(), name='key-import'),

    url(r'^corporations/$', CorporationListView.as_view(), name='corporation-list'),
    url(r'^corporations/(?P<pk>\d+)/$', CorporationDetailView.as_view(), name='corporation-detail'),
    url(r'^corporations/(?P<pk>\d+)/contact/$', CorporationUpdateContactView.as_view(), name='corporation-updatecontact'),
    url(r'^corporations/(?P<pk>\d+)/adjustment/$', ManualAdjustmentView.as_view(), name='corporation-manualadjustment'),
    
    url(r'^totals/(?P<pk>\d+)/charge/$', ChargeTotalView.as_view(), name='total-charge'),
)
