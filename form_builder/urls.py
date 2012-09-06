from django.conf.urls.defaults import patterns, url
from django.views.decorators import csrf

import views

urlpatterns = patterns('',
    url(r'form/create/$', views.FormCreateView.as_view(),
        name='form_builder_form_create'),
    url(r'form/(?P<pk>\d+)/update/$', csrf.csrf_exempt(
        views.FormUpdateView.as_view()), name='form_builder_form_update'),
    url(r'object/create/(?P<form_pk>\d+)/$', views.ObjectCreateView.as_view(),
        name='form_builder_object_create'),
    url(r'object/(?P<pk>\d+)/update/(?P<form_pk>\d+)/$',
        views.ObjectUpdateView.as_view(),
        name='form_builder_object_update'),
)
