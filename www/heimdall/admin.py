# -*- coding: utf-8 -*-
from django.contrib import admin
from heimdall.models import Server, Permission

admin.site.register(Server)
admin.site.register(Permission)
