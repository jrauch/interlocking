import os
import collections

class Sshconfig:
	def __init__(self, path = os.path.expanduser('~')+"/.ssh/tunconfig"):
		self.path = path
		self.config = collections.OrderedDict()
		self.read_config()

	def read_config(self, setconfig=True):
		f = open(self.path, "r")

		tuns = collections.OrderedDict()
		ntun = None
		while 1:
			line=f.readline()
			if not line:
				break

			if line.strip().startswith("Host "): # end prior, start new
				if ntun != None:
					tuns[ntun["Host"]] = ntun
				ntun = collections.OrderedDict()
				tokens = line.strip().split()
				if tokens:
					if (tokens[0] == '#') and (tokens[1].startswith('tunm:')):
						tokens = tokens[1:len(tokens)]
					ntun[tokens[0]] = " ".join(tokens[1:len(tokens)])
			else:
				# parse lines here
				if not ntun == None:
					tokens = line.strip().split()
					if tokens:
						if (tokens[0] == '#') and (tokens[1].startswith('tunm:')):
							tokens = tokens[1:len(tokens)]
						ntun[tokens[0]] = " ".join(tokens[1:len(tokens)])

		if ntun != None:
			tuns[ntun["Host"]] = ntun
		f.close();
		if setconfig == True:
			self.config = tuns
		return tuns

	def set_config(self, config):
		self.config = config
		return config

	def write_config(self):
		#f = open(self.path, "w")
		for tun in self.config.keys():
			print "{0} {1}".format('Host', self.config[tun]['Host'])
			for key in self.config[tun]:
				if key != 'Host':
					print "{0}{1} {2}".format("# " if key.startswith('tunm') else "", key, self.config[tun][key])
			print ""
		return

	def get_config(self, host):
		if self.config.has_key(host):
			return self.config[host]
		return None

	def is_config(self, host):
		if self.config.has_key(host):
			return True
		return False

	def get_config_value(self, host, value):
		if self.config[host].has_key(value):
			return self.config[host][value]
		return None

	def get_config_source(self, host):
		return self.path

	def get_tunnels(self):
		returnlist = []
		for tun in self.config.keys():
			returnlist.append(tun)
		return returnlist

	def get_autostart(self):
		returnlist = []
		for tun in self.config.keys():
			if (self.config[tun].has_key('tunm:Autoconnect')) and (self.config[tun]['tunm:Autoconnect'] == "true"):
				returnlist.append(self.config[tun])
		return returnlist
