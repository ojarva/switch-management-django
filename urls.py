from django.conf.urls.defaults import patterns, include, url

import os

from django.contrib import admin
admin.autodiscover()

from switch.views import offices, switches, ports, change_port, physical_ports, room, rooms, refresh_from_switch
from ipdb.views import get_macdb, update_mac_ip


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'futurice_switchmanagement.views.home', name='home'),
    # url(r'^futurice_switchmanagement/', include('futurice_switchmanagement.foo.urls')),
    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': 'offices'}),

    url(r'^offices$', offices),
    url(r'^switches/(?P<office_id>.+)$', switches),
    url(r'^rooms/(?P<office_id>.+)$', rooms),
    url(r'^room/(?P<room_id>\d+)$', room),
    url(r'^ports/(?P<switch_id>.+)$', ports),
    url(r'^port/(?P<port_id>\d+)$', change_port),
    url(r'^physical_ports/(?P<office_id>.+)$', physical_ports),
    url(r'^refresh_from_switch/(?P<port_id>\d+)$', refresh_from_switch),
    url(r'^refresh_from_switch$', refresh_from_switch),
    url(r'^api/get_macdb$', get_macdb),
    url(r'^api/update_mac_ip$', update_mac_ip),

    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',  {'document_root': os.path.join(os.path.dirname(__file__), 'static')}),

    url(r'^admin/', include(admin.site.urls)),
)
