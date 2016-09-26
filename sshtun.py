import rumps
import manager
import AppKit
info = AppKit.NSBundle.mainBundle().infoDictionary()
info["LSBackgroundOnly"] = "1"

class sshtunhelper:
	def __init__(self, menu, mgr, tries):
		self.manager = mgr
		self.tries = tries
		self.menu = menu

	def toggletunnelcb(self, sender):
		sender.state = not sender.state
		if sender.state != 0:
			self.manager.start_tunnel(sender.title)
		else:
			self.manager.shutdown_tunnel(sender.title)

	def edittunnelcb(self, sender):
		return

	def deletetunnelcb(self, sender):
		return

	def clonetunnelcb(self, sender):
		return

	def popwin(self, sender):
		win = rumps.Window('computer\'s IP address:port number','Server address',
			default_text="",cancel=True,dimensions=(320,20))
		response = win.run()
		print response
		return

	def timerb(self, sender):
		# call respawner
		# respawner will return a list of tunnels it COULD NOT AND WILL NOT RESTART ANYMORE
		# as well as reaped tunnels not set to restart.
		# get all tunnel states, and adjust the check marks to correspond
		#print "TICK"
		message = ""
		s = self.manager.respawner()
		if len(s["restartfails"]) > 0:
			message = message + "The following tunnels failed to restart: "
			decorate=0
			for rf in s["restartfails"]:
				if decorate != 0:
					message = message + ", "
				message = message + rf
				decorate = decorate + 1
				self.menu["Tunnels"][rf].state = 0
			message = message + "\n"

		if len(s["terminators"]) > 0:
			message = message + "The following items terminated: "
			decorate = 0
			for tr in s["terminators"]:
				if decorate != 0:
					message = message + ", "
				message = message + tr
				self.menu["Tunnels"][tr].state = 0

		if len(message) != 0:
			print message
			rumps.notification(title="SSH Tunnel Alert", subtitle="", message=message, data=None)
			return # popup
		return

class sshtun(rumps.App):
	def __init__(self, m, ic="noun_32768.png", qb=None):
		super(sshtun, self).__init__("sshtun", icon=ic, quit_button = qb)
		self.menu = ["Tunnels", "Create New Tunnel..."]
		self.manager = m
		self.helper = sshtunhelper(self.menu, self.manager, tries = 3) # TRIES SHOULD NOT BE HARDCODED XXX
		self.timer = rumps.Timer(self.helper.timerb, 5)

	def addtunnelitem(self, parent, name, state):
		#sthelper = sshtunhelper(self.manager)
		m = rumps.MenuItem(name, self.helper.toggletunnelcb)
		m.state = state
		self.menu[parent].add(m)
		m = rumps.MenuItem("Edit tunnel...", self.helper.edittunnelcb)
		self.menu['Tunnels'][name].add(m)
		m = rumps.MenuItem("Clone tunnel...", self.helper.clonetunnelcb)
		self.menu['Tunnels'][name].add(m)
		m = rumps.MenuItem("Delete tunnel...", self.helper.deletetunnelcb)
		self.menu['Tunnels'][name].add(m)
		m = rumps.MenuItem("pop tunnel...", self.helper.popwin)
		self.menu['Tunnels'][name].add(m)

		return

	def starttimer(self):
		self.timer.start()

	@rumps.clicked("Quit")
	def quit(self, _):
		self.manager.shutdown_tunnels()
		rumps.quit_application()

if __name__ == "__main__":
	m=manager.Tunnelmanager()
	smenu = sshtun(m,"noun_32768.png", None)
	# list
	for tun in m.list_tunnels():
		smenu.addtunnelitem("Tunnels", tun, 1 if m.is_running(tun) == True else 0)

	smenu.starttimer()
	smenu.run()
