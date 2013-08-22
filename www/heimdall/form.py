# -*- coding: utf-8 -*-
from django import forms

class UploadSshKeyForm(forms.Form):
    docfile = forms.FileField(
        label='Select your key to upload',
        help_text='(max. 42 megabytes, please check your uploading a valid key)'
    )
