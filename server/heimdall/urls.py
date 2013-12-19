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

# Name:         urls.py
# Author:       Vandecappelle Steeve & Sobczak Arnaud
# Copyright:    (C) 2013-2014 Vandecappelle Steeve & Sobczak Arnaud
# Licence:      GNU General Public Licence version 3
# Website:      http://vekia.github.io/heimdall/
# Email:        svandecappelle at vekia.fr
"""

# (r'^heimdall/$', TemplateView.as_view(template_name='index.html'))

from django.conf.urls import patterns, url

import heimdall.admin.views
import heimdall.user.views
import heimdall.servers.views

urlpatterns = patterns('',
	url(r'^$', heimdall.user.views.index, name='index'),
	url(r'^connect$', 'django.contrib.auth.views.login', {'template_name': 'heimdall/connect.html'}),
	url(r'^home$', heimdall.user.views.index, name='index'),
	url(r'^users$', heimdall.user.views.users, name='users'),
	url(r'^servers$', heimdall.servers.views.servers, name='servers'),
	url(r'^login$', heimdall.user.views.user_login),
	url(r'^logout$', heimdall.user.views.user_logout),

	url(r'^user/messages$', heimdall.user.views.inbox, name='inbox'),
	url(r'^user/deposite$', heimdall.user.views.deposite, name='deposite'),
	url(r'^user/require_access$', heimdall.user.views.require_access, name='require_access'),
	url(r'^user/markasread$', heimdall.user.views.mark_as_read),
	url(r'^user/register$', heimdall.user.views.register, name='register'),
	url(r'^user/register_action$', heimdall.user.views.register_action, name='register_action'),
	url(r'^user/permissions$', heimdall.servers.views.permissions, name='permissions'),

	url(r'^admin/install$', heimdall.admin.views.install, name='install'),
	url(r'^admin/user$', heimdall.admin.views.user, name='admin-user'),
	url(r'^admin/permissions$', heimdall.admin.views.permissions, name='admin-permissions'),
	url(r'^admin/grant_access$', heimdall.admin.views.grant_access, name='admin-grant-permission'),
	url(r'^admin/register_user$', heimdall.admin.views.register_user, name='admin-register-user'),
	url(r'^admin/manage_groups$', heimdall.admin.views.manage_groups, name='admin-group-management'),
	url(r'^admin/add_group$', heimdall.admin.views.add_group, name='add-group'),
	url(r'^admin/perimeter_pool$', heimdall.admin.views.perimeter_pool, name='perimeter_pool'),
	url(r'^admin/add_to_group$', heimdall.admin.views.add_to_group, name='add-group'),
	url(r'^admin/manage_user_group$', heimdall.admin.views.manage_user_group, name='manage-user-group'),
	url(r'^admin/create_server$', heimdall.admin.views.create_server, name='create-server'),
	url(r'^admin/manage_user_role$', heimdall.admin.views.manage_user_role, name='manage-user-role'),
	url(r'^admin/revoke_access$', heimdall.admin.views.revoke_access, name='revoke-access'),
	url(r'^admin/manage_role$', heimdall.admin.views.manage_role, name='manage-role'),
	url(r'^admin/manage_group$', heimdall.admin.views.manage_group, name='manage-group'),
	url(r'^admin/app_config$', heimdall.admin.views.app_config, name='app-config'),
	url(r'^admin/app_config_save$', heimdall.admin.views.app_config_save),
)
