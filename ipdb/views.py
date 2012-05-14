"""
IP database views
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

from switch.models import MacDB, IPDB

# port mac timestamp
# port -> number,mode,vlan
def get_macdb(request):
    ret_dict = {"macdb": {}}
    macdb = MacDB.objects.select_related(depth=2).filter(archived=False)
    latest_entry = datetime.datetime.now()-datetime.timedelta(days=365)
    for item in macdb:
        if not item.mac in ret_dict["macdb"]:
            ret_dict["macdb"][item.mac] = []
        if item.timestamp > latest_entry:
            latest_entry = item.timestamp
        ret_dict["macdb"][item.mac].append({'switch': item.port.switch.switch_ip, 'port_number': item.port.number, 'port_mode': item.port.mode, 'vlan': item.port.vlan, 'last_seen': str(item.timestamp), 'first_seen': str(item.first_seen)})
    ret_dict["info"] = {"mac_count": len(ret_dict["macdb"]), "latest_entry": str(latest_entry)}
    return HttpResponse(json.dumps(ret_dict, sort_keys=True, indent=4), content_type="text/plain")

@csrf_exempt
def update_mac_ip(request):
    start_time = datetime.datetime.now()
    ret_dict = {"new_entries_added": 0, "old_entries_updated": 0, "new_entries": []}
    if request.POST.get("arptables"):
        table = json.loads(request.POST.get("arptables"))
        for entry in table:
            # 1. Another mac in same IP -> archived
            ret_dict["duplicate_mac_entries_archived"] = IPDB.objects.filter(ip=entry.get("ip")).exclude(mac=entry.get("mac")).filter(archived=False).update(archived=True)
            # 2. MAC in another IP -> archived
            ret_dict["duplicate_ip_entries_archived"] = IPDB.objects.filter(mac=entry.get("mac")).exclude(ip=entry.get("ip")).filter(archived=False).update(archived=True)
            obj = IPDB.objects.filter(mac=entry.get("mac")).filter(ip=entry.get("ip")).filter(archived=False)
            if len(obj) > 0:
                ret_dict["old_entries_updated"] += 1
                obj = obj[0]
            else:
                obj = IPDB(ip=entry.get("ip"), mac=entry.get("mac"), archived=False)
                ret_dict["new_entries"].append(entry.get("mac"))
                ret_dict["new_entries_added"] += 1
            obj.last_seen = datetime.datetime.now()
            obj.save()
        ret_dict["status"] = "Tables updated"
        ret_dict["success"] = True
    else:
        ret_dict["status"] = "No table specified, no actions taken"
        ret_dict["success"] = False

    # 3. Cleanup: if not seen for > 350 seconds, archive
    ret_dict["too_old_entries_archived"] = IPDB.objects.filter(archived=False).filter(last_seen__lte=datetime.datetime.now()-datetime.timedelta(seconds=350)).update(archived=True)
    # Counters
    ret_dict["number_of_active_entries"] = IPDB.objects.filter(archived=False).count()
    ret_dict["number_of_archived_entries"] = IPDB.objects.filter(archived=True).count()
    ret_dict["number_of_entries"] = ret_dict["number_of_active_entries"] + ret_dict["number_of_archived_entries"]
    end_time = datetime.datetime.now()
    ret_dict["start_time"] = str(start_time)
    ret_dict["end_time"] = str(end_time)
    ret_dict["duration"] = str(end_time-start_time)
    return HttpResponse(json.dumps(ret_dict))
