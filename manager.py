import tunnel
import config

class Tunnelmanager:
    def __init__(self, lconfig=None, lsshargs=None):
        self.tunnels={}
        self.config = config.Sshconfig() if lconfig == None else config.Sshconfig(lconfig)
        self.config.read_config()
        self.start_autotunnels()

    def start_autotunnels(self):
        for tun in self.config.get_autostart():
            self.start_tunnel(tun['Host'], tries = 3)
        return

    def shutdown_tunnels(self):
        keys = self.tunnels.keys()
        for key in keys:
            self.shutdown_tunnel(key)
        return

    def shutdown_tunnel(self, host):
        self.tunnels[host].shutdown_tunnel()
        self.tunnels.pop(host)
        return

    def start_tunnel(self, host, tries=0):
        if self.tunnels.has_key(host) != True:
            if self.config.is_config(host) != True:
                return False
            print "Starting tunnel for {}".format(host)
            if self.config.get_config_value(host, "tunm:Reconnect") == 'true':
                tries = 3 # XXX gross gross gross this should be a config in the app somewhere
                sshtunnel = tunnel.Sshtunnel(host, True, self.config.get_config_source(host), attempts=tries)
                self.tunnels[host] = sshtunnel
            else:
                sshtunnel = tunnel.Sshtunnel(host, False, self.config.get_config_source(host))
                self.tunnels[host] = sshtunnel
        if (self.config.get_config_value(host, "tunm:Reconnect") == 'true'):
            if(self.tunnels[host].attempts !=0 ):
                self.tunnels[host].set_attempts(self.tunnels[host].attempts - 1)
            else:
                return False
        self.tunnels[host].start_tunnel() # handle errors! XXX

        return True

    def is_running(self, host):
        if self.tunnels.has_key(host):
            return self.tunnels[host].is_tunnel_alive()
        return False

    def list_tunnels(self):
        return self.config.get_tunnels()

    def get_states(self):
        returndict = {}
        tunnels = self.config.get_tunnels()
        for tun in tunnels:
            returndict[tun] = self.tunnels[tun].is_tunnel_alive()

    def respawner(self):
        restartfails = []
        terminators = []
        for k,v in self.tunnels.items():
            if not v.is_tunnel_alive(): #When a tunnel IS running AND IS reconnect, just set its attemps back up to 3 XXX
                if v.is_reconnect():
                    if self.start_tunnel(k) == False:# handle errors!
                        self.tunnels.pop(k)
                        restartfails.append(k)
                else:
                    self.tunnels.pop(k)
                    terminators.append(k)
            else:
                v.set_attempts(3) # BAD BAD BAD XXX
        return {'restartfails': restartfails, 'terminators': terminators}
