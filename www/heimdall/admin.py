# -*- coding: utf-8 -*-
from django.contrib import admin
from heimdall.models import User, Server, Permission

admin.site.register(User)
admin.site.register(Server)
admin.site.register(Permission)
