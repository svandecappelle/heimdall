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

# Name:         ReplicationFactory.py
# Author:       Vandecappelle Steeve & Sobczak Arnaud
# Copyright:    (C) 2009-2010 Vandecappelle Steeve & Sobczak Arnaud
# Licence:      GNU General Public Licence version 3
# Website:      http://vekia.github.io/heimdall/
# Email:        svandecappelle at vekia.fr
"""

from sqlite3 import *
from paramiko import *
from email.mime.text import MIMEText
import sys,os,re,socket,smtplib
import pyinotify

from runner import ConfigurationFiles

from lib.utils import Constants
from lib.utils.Logger import Logger
from lib.utils import fileutils

from lib.datas.DataBaseConnector import DataBaseConnector
from lib.datas.RequestBinder import RequestBinder
from lib.datas.RequestBinder import Request


logger = Logger("ReplicationFactory", Constants.DEBUG)

class ReplicationFactory: 

    	def watch(self):
    		'''I am the watcher, I look for a file coming on deposit'''
		watcher = pyinotify.WatchManager()
		watcher.add_watch(Constants.DEPOT,pyinotify.ALL_EVENTS,rec=True)                           
	
		handler = handlerEvent(self)
	
		notifier = pyinotify.Notifier(watcher,handler)
		notifier.loop()
                                                                              
    	def revoke_all_access(self):
    		'''Revoke all access. Note: fonction not yet available'''
		logger.log("Revoke all access (not yet implemented)",Constants.WARN)
		con = connect(Constants.DB_FILE)
		cur = con.cursor()
		try:
		    # Ths query give us a tuple which contain server name, login and username
		    cur.execute("select * from server_permissions")
		    logger.log("Revoked all access (not yet implemented)",Constants.WARN)
		except Exception,e:
		    logger.log("Error occured while retreiving permissions : " + e.args[0] , Constants.ERROR)
		cur.close()
		con.close()

	def replicate_file(self, file_name):
		'''Replicate a permission'''
		length = fileutils.file_len(file_name)
		if length > 1:
			logger.log("Error: file '%s' is not a valid rsa-id file"%file_name, Constants.ERROR)
		else:
			userName=os.path.basename(file_name).split('-',1)[0]
			logger.log("Received key from : " + userName, Constants.INFO)
			
			# Reading and coying the rsa key file
			try:
				file_rsa = open(file_name,'rU')
			except IOError,e:
				logger.log("Can't open file "+file_name, Constants.ERROR)
			else:
				key_rsa = file_rsa.readline()				
			
				### Insert key RSA_ID_PUB to db file for remove access
				insertRsa = RequestBinder.Request("RSA_ID")
				insertRsa.setMode("INSERT")
				insertRsa.addSelect("USER_NAME")
				insertRsa.addSelect("RSA")
			
				insertRsa.addValues(str(userName.upper()))
				insertRsa.addValues(str(key_rsa))
			
				connector = DataBaseConnector.DataBaseConnector(Constants.DB_FILE)
				insertRsaQuery = RequestBinder.RequestBinder(connector)
				insertRsaQuery.execQuery(insertRsa);
				logger.log("Permission added to datafile",Constants.DEBUG)		
			
				self.replicate_key(userName,key_rsa)
				file_rsa.close()

	def replicate_key(self, userName,key_rsa):
		'''Replicate RSA key '''
		con = connect(Constants.DB_FILE)
		cur = con.cursor()
		try:
			# Ths query give us a tuple which contain server name, login and username
			cur.execute("select * from server_permissions where user_name = '%s';"%userName.upper())
			#	print "select * from server_permissions where user_name = '%s';"%userName.upper()
		except Exception,e:
			#no error on DB: try to replicate
			logger.log("Error occured while retreiving permissions : " + e.args[0] , Constants.ERROR)
			    
		logger.log("Looking for available server", Constants.DEBUG)
		rows = cur.fetchall()		
		# if no server permission 
		if len(rows) == 0:
			logger.log("No server permission for user '%s'"%userName.upper(), Constants.WARN)
			    
		# else 
		for permissions in rows :
			# for each permission add a key on the .ssh/authorized_keys file
			srv,user,login = permissions
			# user : is the user to loggin (oracle/jboss...)
			server = str(srv)
			logger.log('For user %s, key is copying on %s as and unix user : %s'%(str(user),server, str(login)), Constants.INFO)
			self.replicate_one_server(server, login ,key_rsa , userName)
    
	def replicate_one_server(self, server,userhost,key_rsa, userName):
		'''Replicate access on one server for one user'''
		try:
			client = SSHClient()
			client.load_system_host_keys()
			client.set_missing_host_key_policy(AutoAddPolicy())
			client.connect('%s'%server,port=Constants.SSH_PORT,username=userhost)    
		
			### Insert permission into server authorized_keys ssh file
			stdin,stdout,stderr = client.exec_command("echo '%s' >> .ssh/authorized_keys"%key_rsa)
			
		except AuthenticationException,e:
			logger.log("Error Authentication: " + str(e), Constants.ERROR)
		except SSHException ,e:
			logger.log("Error SSH: " + str(e), Constants.ERROR)
		except socket.error,e: # be carefull of NO ROUTE TO HOST exception
			logger.log("Error Socket: " + str(e), Constants.ERROR)
		except Exception, e:
			logger.log("Not catched error on replication: ",e, Constants.ERROR)
				 
		client.close()
		self.notify(server,userName,userhost, False)

	def delete_replication(self, server, userhost, key_rsa, userName):
		"""
		Delete a heimdall replication.
		"""
		try:
			client = SSHClient()
			client.load_system_host_keys()
			client.set_missing_host_key_policy(AutoAddPolicy())
			client.connect('%s'%server,port=Constants.SSH_PORT,username=userhost)    
		
			### Insert permission into server authorized_keys ssh file
			sshconfig_file= "~/.ssh/authorized_keys"
			rsa_search = str(key_rsa).replace('\r\n', '').replace('\r', '').replace('\n', '') 
			
			stdin,stdout,stderr = client.exec_command("grep -v '%s' %s > %s.tmp"%(rsa_search,sshconfig_file,sshconfig_file))
			stdin,stdout,stderr = client.exec_command("cat %s > %s.bak"%(sshconfig_file,sshconfig_file))
			stdin,stdout,stderr = client.exec_command("rm %s"%(sshconfig_file))
			stdin,stdout,stderr = client.exec_command("mv %s.tmp %s"%(sshconfig_file,sshconfig_file))
			stdin,stdout,stderr = client.exec_command("rm %s.bak"%(sshconfig_file))
			logger.log("Access revoked", Constants.INFO)
		except AuthenticationException,e:
			logger.log(e, Constants.ERROR)
		except SSHException ,e:
			logger.log(e, Constants.ERROR)
		except socket.error,e: # be carefull of NO ROUTE TO HOST exception
			logger.log(e, Constants.ERROR)
		except Exception, e:
			logger.log("Not catched error on replication: ",e, Constants.ERROR)
				 
		client.close()	
		self.notify(server,userName,userhost, True)

	def notify(self,server,trig,user, isRevoke):
		"""
		Notify the user and admin if config constant is enable to
		"""
		if Constants.notifyAdminByMail:
			logger.log("Notify admin by email", Constants.INFO)
			if isRevoke:
				self.alertToAdmin('An administrator has just revoke access on %s to %s user connected with %s'%(server,trig,user),server);
			else:
				self.alertToAdmin('An administrator has just open access on %s to %s user connected with %s'%(server,trig,user),server);
			
			
		if Constants.notifyUserByEmail:
			logger.log("Notify user by email", Constants.INFO)
			if isRevoke:
				self.alertToUser('An administrator has just revoke access for you account on %s to %s user connected with %s'%(server,trig,user),trig,server);
			else:
				self.alertToUser('An administrator has just open access for you account on %s to %s user connected with %s'%(server,trig,user),trig,server);
			
		logger.log("Replication finished", Constants.INFO)
		                                              
		
	def alertToAdmin(self, message, server):
		'''Alert by email the admins'''
		# Create an html message
		msg = MIMEText(message,'html')

		s = smtplib.SMTP(Constants.heimdallHost)
		
		sender = Constants.heimdallEmail
		recipients = [Constants.administratorEmail] + Constants.ccAdmins
		msg['Subject'] = 'Heimdall notification access to %s' % server
		msg['From'] = sender
		msg['To'] = ", ".join(recipients)
		s.sendmail(sender, recipients, msg.as_string())
		s.quit()
		
	def alertToUser(self, message, trig, server):
		'''Alert by email the user who granted / revoked'''
		userEmail = self.getUserEmail(trig);
		
		s = smtplib.SMTP(Constants.heimdallHost)
		# Create an html message
		msg = MIMEText(message,'html')
		
		sender = Constants.heimdallEmail
		msg['Subject'] = 'Heimdall notification access to %s' % server
		msg['From'] = sender
		msg['To'] = userEmail
		s.sendmail(sender, userEmail, msg.as_string())
		s.quit()
		
	def getUserEmail(self,user):
		'''Return the user email address'''
		connector = DataBaseConnector(Constants.DB_FILE)
		selectUserQuery = RequestBinder(connector)
		selectUserPub = Request("USER")
		selectUserPub.setIsPrint(False)
		selectUserPub.addSelect("EMAIL")
		selectUserPub.addWhere("USER_NAME  = '" + user + "'")
		result = selectUserQuery.execQuery(selectUserPub)
	
		row = result.fetchone()
		try:
			email = str(row[0])
			connector.database.close()
			return email
		except Exception, e:
			logger.error("Failed to get email user: "+ user +"\n"+ str(e))
			

class handlerEvent(pyinotify.ProcessEvent): 
        '''This class monitor file system and wait for CLOSE_WRITE event on directory
		If a file come into directory and pattern name file is like AAA-id_rsa.pub
		(when AAA is the user's trigramme) then the file is recognize as a rsa key, it is parsed
		and his content is copied on respective server.
	'''         
	
	def __init__(self, replicator):
		self.replicator = replicator

	def process_IN_CLOSE_WRITE(self,event):                
		'''I m the watcher'''
		self.replicate(event)

	def replicate(self, event):
		self.replicator.replicate_file(event.pathname)
