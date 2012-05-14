from django.db import models
import datetime
import socket

from switch.switchconfiguration import SwitchConfiguration, SwitchException
from switch.macdatabase import MacTableGetter


def a_get_switchconfiguration(switch, **kwargs):
    switchconf = SwitchConfiguration(switch.switch_ip, switch.switch_username, switch.switch_password, **kwargs)
    return switchconf

class IPDB(models.Model):
    ip = models.IPAddressField()
    mac = models.CharField(max_length=18)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField()
    archived = models.BooleanField(default=False)

    mac_entries = models.ManyToManyField("MacDB")

    def merge_macdb(self):
        mac_entries = MacDB.objects.filter(mac=self.mac).filter(first_seen__lte=self.first_seen).filter(timestamp__gte=self.last_seen)
        for entry in mac_entries:
            self.mac_entries.add(entry)

    def __unicode__(self):
        return "%s - %s (archived=%s)" % (self.ip, self.mac, self.archived)

class MacDB(models.Model):
    """ MAC database """

    port = models.ForeignKey('Port')
    mac = models.CharField(max_length=18)
    timestamp = models.DateTimeField(auto_now=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    updated = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s - %s" % (self.port, self.mac)

#    class Meta:
#        unique_together = (('port', 'mac'),)


class Switch(models.Model):
    """ Switches. Represents single switch and login credentials """

    switch_ip = models.IPAddressField(primary_key=True)
    switch_name = models.CharField(max_length=50, unique=True)
    switch_username = models.CharField(max_length=50, default="admin")
    switch_password = models.CharField(max_length=50)
    snmp_community = models.CharField(max_length=40, null=True, blank=True)
    only_snmp = models.BooleanField(default=False)
    office = models.ForeignKey('Office')

    class Meta:
        verbose_name_plural = "switches"

    def refresh_mac(self):
        """ Refresh MAC database from switch """
        mactable = MacTableGetter(self.switch_ip, self.snmp_community)
        entries = mactable.get_table()
        for item in entries["by_port"]:
            MacDB.objects.filter(port__switch=self).filter(port__number=item).update(updated=False)
            port = Port.objects.filter(switch=self).filter(number=item)
            if len(port) > 0:
                port = port[0]
            else:
                continue
            for macentry in entries["by_port"][item]:
                macinfo_items = MacDB.objects.filter(port=port).filter(mac=macentry).filter(archived=False)
                if len(macinfo_items) > 0:
                    macinfo = macinfo_items[0]
                else:
                    (macinfo, created) = MacDB.objects.get_or_create(port=port, mac=macentry)
                macinfo.updated = True
                macinfo.save()

            # Remove trunk ports that are not active anymore
            MacDB.objects.filter(port__switch=self).filter(port__number=item).filter(updated=False).filter(archived=False).filter(port__mode='T').delete()
            # Archive non-active ports (access and wlan boxes)
            MacDB.objects.filter(port__switch=self).filter(port__number=item).filter(updated=False).update(archived=True)


    def refresh_from_switch(self):
        """ Refresh VLAN numbers and descriptions from switch """
        if self.only_snmp:
            return
        switchconf = a_get_switchconfiguration(self)
        conf = switchconf.get_configurations()
        for item in conf["vlan"]:
            port = Port.objects.filter(switch=self, number=item)[0]
            port.vlan = conf["vlan"][item]
            port.save()
        for item in conf["descriptions"]:
            port = Port.objects.filter(switch=self, number=item)[0]
            port.description = conf["descriptions"][item]
            port.save()
        switchconf.commit()
        switchconf.logout()


    def __unicode__(self):
        return "%s (%s)" % (self.switch_name, self.switch_ip)

class Office(models.Model):
    office_name = models.CharField(max_length=50, primary_key=True)

    def refresh_mac(self):
        switches = Switch.objects.filter(office=self)
        for switch in switches:
            switch.refresh_mac()

    def refresh_from_switch(self):
        switches = Switch.objects.filter(office=self)
        for switch in switches:
            switch.refresh_from_switch()

    def __unicode__(self):
        return self.office_name

class Room(models.Model):
    office = models.ForeignKey('Office')
    name = models.CharField(max_length=50)

    def refresh_from_switch(self):
        ports = PhysicalPort.objects.filter(room=self)
        for physicalport in ports:
            physicalport.refresh_from_switch()

    def bulk_change(self, vlan, **kwargs):
        change_locked = kwargs.get("change_locked", False)
        change_default = kwargs.get("change_default", False)
        ports = PhysicalPort.objects.filter(room=self)
        switchconfs = {}
        for physicalport in ports:
            if not change_locked:
                if physicalport.port.locked:
                    continue
            if physicalport.port.switch.switch_ip not in switchconfs:
                switchconfs[physicalport.port.switch.switch_ip] = a_get_switchconfiguration(physicalport.port.switch)

            physicalport.change_vlan(vlan, switchconfs[physicalport.port.switch.switch_ip])
            if change_default:
                physicalport.port.default_vlan = vlan
                physicalport.port.save()
                physicalport.save()

        for switch in switchconfs:
            switchconfs[switch].commit()
            switchconfs[switch].logout()

    def __unicode__(self):
        return "%s - %s" % (self.office, self.name)


class Port(models.Model):
    PORT_MODES = (('T', 'Trunk'),
                  ('S', 'Single (access port)'),
                  ('M', 'Multi (not trunk, but multiple computers)'))
    switch = models.ForeignKey('Switch')
    number = models.IntegerField()
    vlan = models.IntegerField(null=True, blank=True, default=3)
    description = models.CharField(max_length=100, null=True, blank=True)
    default_vlan = models.IntegerField(default=3)
    expires = models.DateTimeField(null=True, blank=True)
    locked = models.BooleanField(default=False, help_text="Port should be locked when it's reserved for special use")
    mode = models.CharField(choices=PORT_MODES, max_length=1)

    def change_vlan(self, vlan, switchconf_r = None):
        if switchconf_r is None:
            switchconf = a_get_switchconfiguration(self.switch)
        else:
            switchconf = switchconf_r
        if self.mode == "T":
            return
        switchconf.change_port_vlan(self.number, vlan)
        self.vlan = vlan
        if self.vlan == self.default_vlan:
            self.expires = None
        self.save()
        if switchconf_r is None:
            switchconf.commit()
            switchconf.logout()

    def change_description(self, description, switchconf_r = None):
        if description is None:
            return
        if len(description) == 0:
            description = "-"
        if switchconf_r is None:
            switchconf = a_get_switchconfiguration(self.switch)
        else:
            switchconf = switchconf_r
        switchconf.change_port_description(self.number, description)
        self.description = description
        self.save()
        if switchconf_r is None:
            switchconf.commit()
            switchconf.logout()

    def refresh_from_switch(self, switchconf_r = None):
        if switchconf_r is None:
            switchconf = a_get_switchconfiguration(self.switch)
        else:
            switchconf = switchconf_r
        conf = switchconf.get_configurations()
        if port_id in conf["vlan"]:
            self.vlan = conf["vlan"][port_id]
        if port_id in conf["descriptions"]:
            self.description = conf["description"][port_id]
        self.save()
        if switchconf_r is None:
            switchconf.logout()

    
    def __unicode__(self):
        return "%s (%s (def: %s)) @ %s"% (self.number, self.vlan, self.default_vlan, self.switch)

    class Meta:
        unique_together = (('switch', 'number'),)
        ordering = ["switch__switch_name","number"]

class PhysicalPort(models.Model):
    port = models.ForeignKey('Port')
    room = models.ForeignKey('Room', null=True, blank=True)
    name = models.CharField(max_length=100)
    remarks = models.CharField(max_length=200, null=True, blank=True)

    def refresh_from_switch(self, switchconf_r = None):
        self.port.refresh_from_switch(switchconf_r)

    def change_vlan(self, vlan, switchconf_r = None):
        self.port.change_vlan(vlan, switchconf_r)

    def change_description(self, description, switchconf_r):
        self.port.description(description, switchconf_r)

    class Meta:
        ordering = ["name"]

    def __unicode__(self):
        return "%s - %s" % (self.name, self.port)

class PortLog(models.Model):
    port = models.ForeignKey('Port')
    username = models.CharField(max_length=20)
    message = models.CharField(max_length=300)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]

    def __unicode__(self):
        return "%s - %s - %s" % (self.port, self.created, self.message)

class RoomLog(models.Model):
    room = models.ForeignKey('Room')
    username = models.CharField(max_length=20)
    message = models.CharField(max_length=300)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]

    def __unicode__(self):
        return "%s - %s - %s" % (self.room, self.created, self.message)
