#!/bin/bash
# -*- coding:UTF8 -*-
    
source bin/activate
gunicorn_django /usr/share/replicator/heimdall/server/ --bind 127.0.0.1:8080 --log-file /var/log/www/heimdall.gunicorn.log --log-level debug
