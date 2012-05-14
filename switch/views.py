"""
Switch management views
"""
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

import datetime
import json
import pickle

from switch.models import Room, Office, Switch, Port, PhysicalPort, RoomLog, PortLog
from switch.forms import BulkChangeForm, PortForm, EmptyForm
from switch.switchconfiguration import SwitchException

def log_port_action(request, **kwargs):
    a = PortLog(message=kwargs.get("message"), username=request.user.username)
    if kwargs.get("port") is not None:
        a.port = kwargs.get("port")
    a.save()

def log_room_action(request, **kwargs):
    a = RoomLog(message=kwargs.get("message"), username=request.user.username)
    if kwargs.get("room") is not None:
        a.room = kwargs.get("room")
    a.save()

def handle_switchexception(request, e):
    if e.clear_crash:
         messages.error(request, e.message)
    else:
         messages.critical(request, e.message)

@login_required
def refresh_from_switch(request, port_id = None):
    ret_dict = {}
    if request.method == 'POST':
        form = EmptyForm(request.POST)
        if form.is_valid():
            if port_id is None:
                aswitches = Switch.objects.all()
                for switch in aswitches:
                    switch.refresh_from_switch()
                    ports = Port.objects.filter(switch=switch)
                    for item in ports:
                        log_port_action(request, message="Refreshed from switch", port=item)
                    messages.info("Refreshed all ports on switch %s" % switch)
            else:
                aport = get_object_or_404(Port, id=port_id)
                aport.refresh_from_switch()
                log_port_action(request, message="Refreshed from switch", port=aport)
                messages.info("Refreshed port %s from switch" % aport)

    return render_to_response("refresh_from_switch.html", ret_dict, context_instance=RequestContext(request))

@login_required
def offices(request):
    ret_dict = {}
    aoffices = Office.objects.all().order_by('office_name')
    ret_dict["offices"] = aoffices
    return render_to_response("offices.html", ret_dict, context_instance=RequestContext(request))

@login_required
def room(request, room_id):
    ret_dict = {}
    aroom = get_object_or_404(Room, id=room_id)
    ret_dict["room"] = aroom
    ports = PhysicalPort.objects.filter(room=aroom)

    if request.method == 'POST':
        form = BulkChangeForm(request.POST)
        if form.is_valid():
            try:
                aroom.bulk_change(form.cleaned_data['vlan'], change_default=form.cleaned_data.get("change_default", False), change_locked=form.cleaned_data.get("change_locked", False))
                log_room_action(request, message="Changed all ports to %s" % form.cleaned_data['vlan'], room=aroom)
                for aport in ports:
                    log_port_action(request, message="Changed to vlan %s" % form.cleaned_data['vlan'], port=aport.port)
                messages.info("Changed all ports to %s (room %s)" % (form.cleaned_data["vlan"], aroom))
            except SwitchException as e:
                handle_switchexception(request, e)
            #Re-fetch ports with up-to-date information.
            ports = PhysicalPort.objects.filter(room=aroom)
            
    else:
        form = BulkChangeForm()

    ret_dict["form"] = form
    ret_dict["ports"] = ports
    return render_to_response("room.html", ret_dict, context_instance=RequestContext(request))

@login_required
def rooms(request, office_id):
    ret_dict = {}
    aoffice = get_object_or_404(Office, office_name=office_id)
    ret_dict["office"] = aoffice
    rooms = Room.objects.filter(office=aoffice).order_by('name')
    ret_dict["rooms"] = rooms
    return render_to_response("rooms.html", ret_dict, context_instance=RequestContext(request))

@login_required
def switches(request, office_id):
    ret_dict = {}
    aoffice = get_object_or_404(Office, office_name=office_id)
    ret_dict["office"] = aoffice
    switches = Switch.objects.filter(office=aoffice).order_by('switch_name')
    ret_dict["switches"] = switches
    return render_to_response("switches.html", ret_dict, context_instance=RequestContext(request))

@login_required
def ports(request, switch_id):
    ret_dict = {}
    aswitch = get_object_or_404(Switch, switch_ip=switch_id)
    ret_dict["switch"] = aswitch
    ports = Port.objects.filter(switch=aswitch).order_by('number')
    ret_dict["ports"] = ports
    return render_to_response("ports.html", ret_dict, context_instance=RequestContext(request))

@login_required
def change_port(request, port_id):
    ret_dict = {}
    aport = get_object_or_404(Port, id=port_id)
    ret_dict["port"] = aport
    if request.method == 'POST':
        form = PortForm(request.POST, instance=aport)
        if form.is_valid():
            try:
                aport.change_vlan(form.cleaned_data["vlan"])
                log_port_action(request, port=aport, message="Changed port vlan to %s" % form.cleaned_data["vlan"])
            except SwitchException as e:
                handle_switchexception(request, e)
            try:
                aport.change_description(form.cleaned_data["description"])
                log_port_action(request, port=aport, message="Changed port description to %s" % form.cleaned_data["description"])
            except SwitchException as e:
                handle_switchexception(request, e)
            aport = get_object_or_404(Port, id=port_id)
            ret_dict["port"] = aport
    else:
        form = PortForm(instance=aport)
    physicalport = PhysicalPort.objects.filter(port=aport)
    if len(physicalport) > 0:
        ret_dict["physicalport"] = physicalport[0]
    ret_dict["form"] = form
    ret_dict["expire_date"] = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    return render_to_response("change_port.html", ret_dict, context_instance=RequestContext(request))

@login_required
def physical_ports(request, office_id):
    ret_dict = {}
    office = get_object_or_404(Office, office_name=office_id)
    ports = PhysicalPort.objects.filter(port__switch__office=office).order_by('name')
    ret_dict["office"] = office
    ret_dict["ports"] = ports
    return render_to_response("physical_ports.html", ret_dict, context_instance=RequestContext(request))


