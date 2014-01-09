import threading


from tasks import add


class RefreshingServersHosts():

	def __init__(self):
		#init
		print("init")

	def run(self):
		add.delay(2, 2)


#class RefreshingServersHosts(threading.Thread):
#
#	def __init__(self):
#		threading.Thread.__init__(self)
#		HostedUsers.objects.all().delete()
#
#	def run(self):
#		if not PendingThread.objects.filter(process='userhost-list-refresh').exists():
#			servers = Server.objects.all()
#			thread = PendingThread(process='userhost-list-refresh', pending_request=servers.count())
#			thread.save()
#			time.sleep(10)
#			#for server in servers:
#			#	appendedUsers = utils.getAvailableUsersInHost(server)
#
#			#for user in appendedUsers:
#			#	userHost = HostedUsers(server=server, username=user)
#			#	userHost.save()
#
#			thread.delete()
