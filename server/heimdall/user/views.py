#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

This file is part of Heimdall.

Heimdall is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Heimdall is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Heimdall.  If not, see <http://www.gnu.org/licenses/>.

Authors:
- Vandecappelle Steeve<svandecappelle@vekia.fr>
- Sobczak Arnaud<asobczack@vekia.fr>

# Name:         user/views.py
# Author:       Vandecappelle Steeve & Sobczak Arnaud
# Copyright:    (C) 2013-2014 Vandecappelle Steeve & Sobczak Arnaud
# Licence:      GNU General Public Licence version 3
# Website:      http://vekia.github.io/heimdall/
# Email:        svandecappelle at vekia.fr
"""


from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from heimdall import utils
from heimdall.form import UploadSshKeyForm
from heimdall.models import Server, Permission, Demands, SshKeys
from heimdall.objects import Statistics

from heimdall.bastion.runner import Controller

import logging

logger = logging.getLogger("ViewUser")

# HTTP views

# View deposite RSA


def deposite(request):
    '''
    Deposite a new rsa key.
    '''
    userConnected = request.user
    # Handle file upload
    docfile = []
    if request.method == 'POST':
        if request.POST['type'] == 'update':
            keysend = request.POST['key']
            if keysend != "":
                sshkey = None
                if SshKeys.objects.filter(user=userConnected).count() > 0:
                    sshkey = SshKeys.objects.get(user=userConnected)
                    sshkey.key = keysend
                else:
                    sshkey = SshKeys(user=userConnected, key=keysend)
    
                sshkey.save()
    
                err = Controller.revokeAllKeys(Permission.objects.filter(user=request.user), userConnected, sshkey)
                if err is None:
                    err = Controller.replicateAllKeys(Permission.objects.filter(user=request.user), userConnected, sshkey)
    
                    if err is None:
                        message = 'Please wait a minute to connect, during the replication on all server finished. Check your mails to know the access updates'
                    else:
                        message = err.message
                else:
                    message = err.message
                messages.success(request, message)
                # Redirect to the document list after POST
                return HttpResponseRedirect(reverse('deposite'))
            else:
                messages.success(request, "SSH key is not valid")
                return HttpResponseRedirect(reverse('deposite'))
        else:
            form = UploadSshKeyForm(request.POST, request.FILES)
            if form.is_valid():
                docfile = request.FILES['docfile']
                for line in docfile:
                    if SshKeys.objects.filter(user=userConnected).count() > 0:
                        sshkey = SshKeys.objects.get(user=userConnected)
                        sshkey.key = line
                        sshkey.save()

                        err = Controller.revokeAllKeys(Permission.objects.filter(user=request.user), userConnected, sshkey)
                        if err is None:
                            err = Controller.replicateAllKeys(Permission.objects.filter(user=request.user), userConnected, sshkey)

                            if err is None:
                                message = 'Please wait a minute to connect, during the replication on all server finished. Check your mails to know the access updates'
                            else:
                                message = err.message
                        else:
                            message = err.message
                        messages.success(request, message)
                    else:
                        sshkey = SshKeys(user=userConnected, key=line)
                        sshkey.save()

                        err = Controller.revokeAllKeys(Permission.objects.filter(user=request.user), userConnected, sshkey)
                        if err is None:
                            err = Controller.replicateAllKeys(Permission.objects.filter(user=request.user), userConnected, sshkey)

                            if err is None:
                                message = 'Please wait a minute to connect, during the replication on all server finished. Check your mails to know the access updates' 
                            else:
                                message = err.message
                        else:
                            message = err.message
                        messages.success(request, message)
                # Redirect to the document list after POST
                return HttpResponseRedirect(reverse('deposite'))
    else:
        if SshKeys.objects.filter(user=userConnected).count() > 0:
            key = SshKeys.objects.get(user=userConnected).key
        else:
            key = ''

        form = UploadSshKeyForm()

    args = utils.give_arguments(request.user, 'Depot')
    args.update({'documents': docfile, 'form': form, 'key': key})
    return render_to_response('user/deposite.html', args, context_instance=RequestContext(request))


def inbox(request):
    '''
    View demands inbox
    '''
    logger.debug("See inbox")
    demands = utils.get_demands_filtered(request.user)
    args = utils.give_arguments(request.user, 'Messages')
    demands_read = utils.get_demands_filtered_and_read(request.user)
    args.update({'demands': demands, 'demands_read': demands_read})
    return render_to_response('user/messages.html', args, context_instance=RequestContext(request))


def index(request):
    '''
    View Home
    '''
    user_count = Group.objects.get(name="heimdall").user_set.all().count()
    user_count += Group.objects.get(name="heimdall-admin").user_set.all().count()
    server_count = Server.objects.all().count()
    keys_count = SshKeys.objects.all().count()
    demands_count = Demands.objects.filter(close_date__isnull=True).all().count()

    permissions_count = Permission.objects.all().count()
    stats = Statistics(user_count, server_count, permissions_count, demands_count, keys_count)

    args = utils.give_arguments(request.user, 'Acceuil')
    args.update({'stats': stats, 'demands': utils.get_demands_filtered_pending(request.user)})

    return render_to_response('index.html', args, context_instance=RequestContext(request))


def register(request):
    '''
    View register user
    '''
    args = utils.give_arguments(request.user, 'Register')
    return render_to_response('user/register.html', args, context_instance=RequestContext(request))


def users(request):
    '''
    View users
    '''
    if request.user.groups.filter(name="heimdall-admin"):
        list_users = User.objects.all()
    else:
        list_users = [request.user]

    args = utils.give_arguments(request.user, 'Utilisateurs')
    args.update({'list_users': list_users})

    return render_to_response('users.html', args, context_instance=RequestContext(request))


def user_login(request):
    '''
    HTTPS POST forms
    '''
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                # success
                messages.success(request, 'Logged in')
                return HttpResponseRedirect(reverse('index'))
            else:
                messages.success(request, 'Your account was disabled by administrator. Please contact an administrator.')
                return HttpResponseRedirect(reverse('index'))
        else:
            # invalid login
            messages.success(request, 'Wrong username or password.')
            return HttpResponseRedirect(reverse('index'))
    else:
        messages.success(request, 'This page is not accessible.')
        return HttpResponseRedirect(reverse('index'))


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('home')


def mark_as_read(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            hostuser = request.POST['hostuser']
            hostname = request.POST['hostname']
            server = Server.objects.get(hostname=hostname)

            if Demands.objects.filter(user=request.user, server=server, hostuser=hostuser).exists():
                demand = Demands.objects.get(user=request.user, server=server, hostuser=hostuser)
                demand.markAsIgnore = True
                demand.save()
            else:
                messages.success(request, 'You are not the user who made the demand, you cannot mark it as read.')
        else:
            messages.success(request, 'User registered successfully.')
    else:
        messages.success(request, 'This page is not accessible.')
    return HttpResponseRedirect(reverse('inbox'))


def register_action(request):
    if request.method == 'POST':
        messages.success(request, 'User registered successfully.')
        return HttpResponseRedirect(reverse('index'))

    else:
        messages.success(request, 'This page is not accessible.')
        return HttpResponseRedirect(reverse('index'))


def require_access(request):
    if request.method == 'POST':
        userConnected = request.user
        if userConnected.is_authenticated:
            serverHost = Server.objects.get(hostname=request.POST['server'])
            userHost = request.POST['user']

            if userHost == "":
                messages.success(request, 'You must write a user host')
                return HttpResponseRedirect(reverse('servers'))
            elif Demands.objects.filter(user=request.user, server=serverHost, hostuser=userHost).exists():
                messages.success(request, 'Your demand is already pending from manager validation please wait.')
                return HttpResponseRedirect(reverse('servers'))
            elif Permission.objects.filter(user=userConnected, server=serverHost, hostuser=userHost).exists():
                messages.success(request, 'You already granted for access this server and account.')
                return HttpResponseRedirect(reverse('servers'))

            priority = request.POST['priority']
            comments = request.POST['comments']
            cdate = datetime.today()
            demand = Demands(user=userConnected, server=serverHost, hostuser=userHost, priority=priority, comments=comments, cdate=cdate)
            demand.markAsIgnore = False
            demand.save()

            messages.success(request, 'Notification sent to an heimdall administrator.')
            return HttpResponseRedirect(reverse('servers'))
        else:
            messages.success(request, 'You need to be connected to see this page.')
            return HttpResponseRedirect(reverse('index'))
    else:
        messages.success(request, 'This page is not accessible.')
        return HttpResponseRedirect(reverse('index'))
