from __future__ import absolute_import

from celery import shared_task

from heimdall.models import Server, PendingThread, HostedUsers
from heimdall import utils


@shared_task
def refreshUserHosts():

	if not PendingThread.objects.filter(process='userhost-list-refresh').exists():
		HostedUsers.objects.all().delete()

		servers = Server.objects.all()
		thread = PendingThread(process='userhost-list-refresh', pending_request=servers.count())
		thread.save()

		for server in servers:
			appendedUsers = utils.getAvailableUsersInHost(server)
			print(appendedUsers)
			for user in appendedUsers:
				userHost = HostedUsers(server=server, username=user)
				userHost.save()

			thread.pending_request = thread.pending_request - 1
			thread.save()

		thread.delete()
