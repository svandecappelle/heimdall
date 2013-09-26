# -*- coding: utf-8 -*-

from django.contrib import messages
from django.template import RequestContext
from django.shortcuts import render_to_response

from heimdall import utils
from heimdall.models import Server, Permission


def servers(request):
    list_servers = Server.objects.all()
    args = utils.give_arguments(request.user, 'Serveurs')
    args.update({'list_servers': list_servers})

    return render_to_response('servers.html', args, context_instance=RequestContext(request))
    
def permissions(request):
    all_permissions = Permission.objects.all()
    userConnected = request.user

    args = utils.give_arguments(request.user, 'Permissions')
    if userConnected.is_authenticated:
        if userConnected.groups.filter(name="heimdall-admin"):
            args.update({'permissions': convertToIterable(all_permissions)})
        elif userConnected.groups.filter(name="heimdall"):
            permissions_visible = Permission.objects.get(user=userConnected)
            args.update({'permissions': convertToIterable(permissions_visible)})
    return render_to_response('permissions.html', args, context_instance=RequestContext(request))



def convertToIterable(permissions_visible):
    try:
        some_object_iterator = iter(permissions_visible)
        permissions_visible_to_return = permissions_visible
    except TypeError:
        permissions_visible_to_return = [1]
        permissions_visible_to_return[0] = permissions_visible

    return permissions_visible_to_return
