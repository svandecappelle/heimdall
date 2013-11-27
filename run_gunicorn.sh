#!/bin/bash
# -*- coding:UTF8 -*-
    
#source bin/activate
gunicorn_django server/ --bind 127.0.0.1:8000
