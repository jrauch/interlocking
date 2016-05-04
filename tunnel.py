import subprocess, shlex, os

class Sshtunnel:
    def __init__(self, host=None, recon=False, path = os.path.expanduser('~')+"/.ssh/tunconfig", ssh_launchoptions="-N", ssh_bin="/usr/bin/ssh", attempts=0):
        self.ssh_configpath = path
        self.reconnect = recon
        self.ssh_launchoptions = ssh_launchoptions
        self.ssh_bin = ssh_bin
        self.process_handle = None
        self.tunnelname = host
        self.attempts=attempts
        return

    def set_attempts(self, count):
        self.attempts = count
        
    def start_tunnel(self):
        if self.is_tunnel_alive() != True:
            ssh_proc = shlex.split("{0} -F {1} {2} {3}".format(self.ssh_bin, self.ssh_configpath, self.ssh_launchoptions, self.tunnelname))
            self.process_handle = subprocess.Popen(ssh_proc) # you should handle errors XXX
        return

    def is_reconnect(self):
        return self.reconnect

    def is_tunnel_alive(self):
        if (self.process_handle == None):
            return False
        if (self.process_handle.poll() != None):
            return False
        return True

    def shutdown_tunnel(self):
        if (self.process_handle != None):
            p = self.process_handle.terminate()
            return self.process_handle.poll()
        return None

    def kill_tunnel(self):
        try:
            if self.is_tunnel_alive() == True:
                p = self.process_handle.kill()
        finally:
            None
        return self.process_handle.poll()
