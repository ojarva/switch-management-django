from django.conf.urls.defaults import patterns, include, url

import os

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': 'offices'}),

    url(r'^offices$', 'switch.views.offices'),
    url(r'^switches/(?P<office_id>.+)$', 'switch.views.switches'),
    url(r'^rooms/(?P<office_id>.+)$', 'switch.views.rooms'),
    url(r'^room/(?P<room_id>\d+)$', 'switch.views.room'),
    url(r'^ports/(?P<switch_id>.+)$', 'switch.views.ports'),
    url(r'^port/(?P<port_id>\d+)$', 'switch.views.change_port'),
    url(r'^physical_ports/(?P<office_id>.+)$', 'switch.views.physical_ports'),
    url(r'^refresh_from_switch/(?P<port_id>\d+)$', 'switch.views.refresh_from_switch'),
    url(r'^refresh_from_switch$', 'switch.views.refresh_from_switch'),
    url(r'^api/get_macdb$', 'ipdb.views.get_macdb'),
    url(r'^api/update_mac_ip$', 'ipdb.views.update_mac_ip'),

    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',  {'document_root': os.path.join(os.path.dirname(__file__), 'static')}),

    url(r'^admin/', include(admin.site.urls)),
)
