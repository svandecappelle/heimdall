from __future__ import absolute_import

from celery import shared_task

from heimdall.models import Server, PendingThread
import time


@shared_task
def add(x, y):

	if not PendingThread.objects.filter(process='userhost-list-refresh').exists():
		servers = Server.objects.all()
		thread = PendingThread(process='userhost-list-refresh', pending_request=servers.count())
		thread.save()

		for server in servers:
			time.sleep(5)
			thread.pending_request = thread.pending_request - 1
			thread.save()

		#	appendedUsers = utils.getAvailableUsersInHost(server)
		#	#for user in appendedUsers:
		#	userHost = HostedUsers(server=server, username=user)
		#	userHost.save()
		thread.delete()

	return x + y


@shared_task
def mul(x, y):
	return x * y


@shared_task
def xsum(numbers):
	return sum(numbers)
