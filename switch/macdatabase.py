import sys
sys.path.append("/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages")
import subprocess


class MacTableGetter:
    def __init__(self, ip, community):
        self.ip = ip
        self.community = community

    def get_table(self):
        p = subprocess.Popen(["snmpwalk", "-v1", "-c", self.community, self.ip, 'iso.3.6.1.2.1.17.4.3.1.1'], stdout=subprocess.PIPE)
        (a, _) = p.communicate()
        a = a.split("\n")
        p = subprocess.Popen(["snmpwalk", "-v1", "-c", self.community, self.ip, 'iso.3.6.1.2.1.17.4.3.1.2'], stdout=subprocess.PIPE)
        (b, _) = p.communicate()
        b = b.split("\n")
        macdict = {}
        for item in a:
            tmp = item.strip().replace("SNMPv2-SMI::mib-2.17.4.3.1.1.", "").split(" = ")
            if len(tmp) == 2 and "Hex-STRING" in tmp[1]:
                tmp[1] = tmp[1].replace("Hex-STRING: ", "").strip().replace(" ", ":")
                macdict[tmp[0]] = {"mac": (tmp[1]).lower()}
        for item in b:
            tmp = item.strip().replace("SNMPv2-SMI::mib-2.17.4.3.1.2.", "").split(" = ")
            if tmp[0] in macdict and "INTEGER: " in tmp[1]:
                try:
                    tmp[1] = int(tmp[1].replace("INTEGER: ", ""))
                    macdict[tmp[0]]["port"] = tmp[1]
                except:
                    pass
        macdict_finalized = {"by_port": {}, "by_mac": {}}
        for item in macdict:
            if not macdict[item].get("port"):
                continue
            if macdict[item].get("port") not in macdict_finalized['by_port']:
                macdict_finalized["by_port"][macdict[item]['port']] = []
            macdict_finalized["by_port"][macdict[item]['port']].append(macdict[item]['mac'])
            macdict_finalized['by_mac'][macdict[item]['mac']] = macdict[item]['port']
        return macdict_finalized
 
if __name__ == '__main__':
    a = MacTableGetter('10.4.0.19', 'ea8Dooko')
    print a.get_table()
