# -*- coding: utf-8 -*-
from django.contrib import admin
from heimdall.models import Server, Permission, Demands, Roles, RolePerimeter, UserRoles, SshKeys

admin.site.register(Server)
admin.site.register(Permission)
admin.site.register(Demands)
admin.site.register(Roles)
admin.site.register(RolePerimeter)
admin.site.register(UserRoles)
admin.site.register(SshKeys)