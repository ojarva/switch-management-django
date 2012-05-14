
import re
import time
import telnetlib
import sys
import socket
import logging
logger = logging.getLogger(__name__)

class SwitchException(Exception):
    """ Raised when there's an error during communicating with a switch.

    clear_crash is true when switch state is known (for example timeouts during connect/login), false
                   when some operation failed, and state is not committed, and it might be unstable.
    """
    def __init__(self, clear_crash, message):
        logger.debug("Created SwitchException: clear_crash=%s; message=%s" % (clear_crash, message))
        self.clear_crash = clear_crash
        self.message = message

class SwitchConfiguration:
    """ Switch configuration program for Powerconnect 5448 switches. Assumes VLAN is configured as access. """

    def read_all_eager(self):
        a = self.tn.read_eager()
        while a != '':
            a = self.tn.read_eager()

    def connect(self, ip, username, password):
        logger.debug("Connecting to %s..." % ip)

        try:
            self.tn = telnetlib.Telnet(ip, 23, 1)
        except socket.timeout:
            raise SwitchException(True, "Opening connection to %s timed out" % ip)
        except socket.gaierror as e:
            num, expl = e
            raise SwitchException(True, "Opening connection to %s failed: %s" % (ip, expl))
        except socket.error as e:
            num, expl = e
            raise SwitchException(True, "Opening connection to %s failed: %s" % (ip, expl))

        a = self.tn.read_until("User Name:", 1)
        if len(a) == 0:
            raise SwitchException(True, "Waiting for username prompt failed")
        self.read_all_eager()
        self.tn.write(str(username)+"\n")
        self.read_all_eager()
        logger.debug("Username sent to switch %s" % ip)
        a = self.tn.read_until("Password:", 1)
        if len(a) == 0:
            raise SwitchException(True, "Waiting for password prompt failed")
        self.tn.write(str(password)+"\n")
        a = self.tn.read_until("#", 1)
        if len(a) == 0:
            raise SwitchException(True, "Waiting for prompt failed")
        logger.debug("Password sent to switch %s" % ip)
        self.tn.write("terminal datadump\n")
        a = self.tn.read_until("#", 3)
        if len(a) == 0:
            raise SwitchException(True, "Waiting for prompt after datadump setting failed")
        self.config_mode = False
        logger.info("Connected to switch %s" % ip)
        return True

    def __init__(self, ip, username, password):
        self.connected = False
        for i in range(0, 4):
            try:
                if self.connect(ip, username, password):
                     self.connected = True
                     break
            except SwitchException as e:
                pass
        if not self.connected:
            raise e
        self.ip = ip

    def set_config_mode(self, mode):
        logger.debug("Changing config mode to %s for switch %s" % (mode, self.ip))
        """ Change configure mode """
        if self.config_mode is mode:
            logger.debug("Config mode is already %s for switch %s" % (mode, self.ip))
            return
        if mode is True:
            print "Enabling config mode"
            self.tn.write("configure\n")
            self.config_mode = True
        else:
            print "Disabling config mode"
            self.tn.write("end\n")
            self.config_mode = False
        a = self.tn.read_until("#", 3)
        print a
        if len(a) == 0:
            raise SwitchException(True, "Waiting for prompt after setting config mode to %s failed" % mode)
        print self.read_all_eager()


    def change_port_vlan(self, port, vlan):
        logger.info("Changing port %s to vlan %s in switch %s" % (port, vlan, self.ip))
        self.set_config_mode(True)
        port = str(port)
        vlan = str(vlan)
        self.tn.write("interface ethernet g"+port+"\n")
        print self.tn.read_until("#")
        self.tn.write("switchport access vlan "+vlan+"\n")
        print self.tn.read_until("#")
        self.tn.write("exit\n")
        print self.tn.read_until("#")

    def change_port_description(self, port, description):
        description = str(description).strip()
        if len(description) == 0:
            description = "-"
        logger.info("Changing port %s description to %s in switch %s" % (port, description, self.ip))
        self.set_config_mode(True)
        port = str(port)
        self.tn.write("interface ethernet g"+port+"\n")
        print self.tn.read_until("#")
        self.tn.write("description "+description+"\n")
        print self.tn.read_until("#")
        self.tn.write("exit\n")
        print self.tn.read_until("#")

    def commit(self):
        logger.debug("Committing changes in switch %s" % (self.ip))
        self.set_config_mode(False)
        self.tn.write("copy running-config startup-config\n")
        self.tn.read_until("...", 2)
        self.tn.write("y")
        a = self.tn.read_until("#", 8)
        if len(a) == 0:
            raise SwitchException(False, "Copying running-config to startup-config failed due to timeout")

    def logout(self):
        logger.debug("Logging out from switch %s" % (self.ip))
        self.set_config_mode(False)
        self.tn.write("exit\n")
        self.tn = None

    def get_configurations(self):
        logger.debug("Getting configurations in switch %s" % (self.ip))
        self.set_config_mode(False)
        self.tn.write("more running-config\n")
        data = self.tn.read_until("#")
        data = data.split("\n")
        interface_open = False
        description = None
        vlan = None
        vlan_conf = {}
        descriptions = {}
        for line in data:
            if re.match("^exit", line) and interface_open:
                if vlan is not None:
                    for item in interfaces:
                        vlan_conf[item] = vlan
                if description is not None:
                    for item in interfaces:
                        descriptions[item] = description
                interface_open = False
                description = None
                vlan = None
            if interface_open:
                if re.match("^description ", line):
                    description = line.replace("description ", "")
                elif re.match("^switchport access vlan ", line):
                    vlan = int(line.replace("switchport access vlan ", ""))
            if re.match("^interface ethernet", line):
                interfaces = [int(line.replace("interface ethernet g", ""))]
                interface_open = True
            if re.match("^interface range ethernet", line):
                interfaces_tmp = line.replace("interface range ethernet g(", "").replace(")", "").split(",")
                interfaces = []
                for item in interfaces_tmp:
                    if "-" in item:
                        item = item.split("-")
                        for i in range(int(item[0]), int(item[1])+1):
                            interfaces.append(i)
                    else:
                        interfaces.append(item)
        
                interface_open = True

        for interface in range(1, 49):
            if interface not in vlan_conf:
                vlan_conf[interface] = 1
            if interface not in descriptions:
                descriptions[interface] = None

        return {"vlan": vlan_conf, "descriptions": descriptions}


if __name__ == '__main__':
#    switch = SwitchConfiguration("10.4.0.22", "admin", "password")
#    switch.get_configurations()
#    switch.logout()
    print "Disabled. Requires password and username"
