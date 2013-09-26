# (r'^heimdall/$', TemplateView.as_view(template_name='index.html'))

from django.conf.urls import patterns, url

import heimdall.admin.views
import heimdall.user.views
import heimdall.servers.views

urlpatterns = patterns('',
	url(r'^$', heimdall.user.views.index, name='index'),
	url(r'^home$', heimdall.user.views.index, name='index'),
	url(r'^users$', heimdall.user.views.users, name='users'),
	url(r'^messages$', heimdall.user.views.inbox, name='inbox'),
	url(r'^deposite$', heimdall.user.views.deposite, name='deposite'),
	url(r'^connect$', heimdall.user.views.connect, name='connect'),
	url(r'^login$', heimdall.user.views.login),
	url(r'^logout$', heimdall.user.views.logout),
	url(r'^require_access$', heimdall.user.views.require_access, name='require_access'),
	url(r'^register$', heimdall.user.views.register, name='register'),
	url(r'^register_action$', heimdall.user.views.register_action, name='register_action'),
	
	url(r'^servers$', heimdall.servers.views.servers, name='servers'),
	url(r'^permissions$', heimdall.servers.views.permissions, name='permissions'),
	
	url(r'^connect$', 'django.contrib.auth.views.login', {'template_name': 'heimdall/connect.html'}),
	
	url(r'^admin/user$', heimdall.admin.views.user, name='admin-user'),
	url(r'^admin/permissions$', heimdall.admin.views.permissions, name='admin-permissions'),
	url(r'^admin/grant_access$', heimdall.admin.views.grant_access, name='admin-grant-permission'),
	url(r'^admin/register_user$', heimdall.admin.views.register_user, name='admin-register-user'),
	url(r'^admin/manage_groups$', heimdall.admin.views.manage_groups, name='admin-group-management'),
	url(r'^admin/add_group$', heimdall.admin.views.add_group, name='add-group'),
	url(r'^admin/change_perimeter_role$', heimdall.admin.views.change_perimeter_role, name='change-perimeter-role'),
	url(r'^admin/add_to_group$', heimdall.admin.views.add_to_group, name='add-group'),
	url(r'^admin/manage_user_group$', heimdall.admin.views.manage_user_group, name='manage-user-group'),
	url(r'^admin/create_server$', heimdall.admin.views.create_server, name='create-server'),
	url(r'^admin/manage_user_role$', heimdall.admin.views.manage_user_role, name='manage-user-role'),
	url(r'^admin/revoke_access$', heimdall.admin.views.revoke_access, name='revoke-access'),
)
