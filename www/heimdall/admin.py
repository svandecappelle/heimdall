# -*- coding: utf-8 -*-
from django.contrib import admin
from heimdall.models import Server, Permission, Demands

admin.site.register(Server)
admin.site.register(Permission)
admin.site.register(Demands)
