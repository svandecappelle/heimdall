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

# Name:         RequestBinder.py
# Author:       Vandecappelle Steeve & Sobczak Arnaud
# Copyright:    (C) 2013-2014 Vandecappelle Steeve & Sobczak Arnaud
# Licence:      GNU General Public Licence version 3
# Website:      http://vekia.github.io/heimdall/
# Email:        svandecappelle at vekia.fr
"""
import os,sys
import sqlite3
from sqlite3 import dbapi2 as sqlite

from lib.utils import strutils 
from lib.utils.Logger import Logger
from lib.utils import Constants


logger = Logger("RequestBinder")


class RequestBinder:	

   def __init__(self, connection):
	self.connection = connection

   def log_dynamic_columns(self, columns, list_to_display):
	# log column of a tuple
	chaine_col = ""	 
	for i in columns:
		chaine_col = chaine_col +"%-30s"

	size = len(columns)
	if size == 0:
		logger.warn("No column to display - Empty Table")
	elif size ==1:
		logger.info(chaine_col % (list_to_display[0]))
	elif size == 2:
		logger.info(chaine_col % (list_to_display[0], list_to_display[1]))
	elif size == 3: 	
		logger.info(chaine_col % (list_to_display[0], list_to_display[1], list_to_display[2]))
	elif size == 4: 
		logger.info(chaine_col % (list_to_display[0], list_to_display[1], list_to_display[2], list_to_display[3]))
	elif size == 5: 
		logger.info(chaine_col % (list_to_display[0], list_to_display[1], list_to_display[2], list_to_display[3], list_to_display[4]))
	elif size == 6: 
		logger.info(chaine_col % (list_to_display[0], list_to_display[1], list_to_display[2], list_to_display[3], list_to_display[4], list_to_display[5]))
	elif size == 7: 
		logger.info(chaine_col % (list_to_display[0], list_to_display[1], list_to_display[2], list_to_display[3], list_to_display[4], list_to_display[5], list_to_display[6]))
	elif size == 8: 
		logger.info(chaine_col % (list_to_display[0], list_to_display[1], list_to_display[2], list_to_display[3], list_to_display[4], list_to_display[5], list_to_display[6], list_to_display[7]))
	elif size == 9: 
		logger.info(chaine_col % (list_to_display[0], list_to_display[1], list_to_display[2], list_to_display[3], list_to_display[4], list_to_display[5], list_to_display[6], list_to_display[7], list_to_display[8]))
	elif size == 10: 
		logger.info(chaine_col % (list_to_display[0], list_to_display[1], list_to_display[2], list_to_display[3], list_to_display[4], list_to_display[5], list_to_display[6], list_to_display[7], list_to_display[8], list_to_display[9]))
	else:
		logger.warn("Too high column number in table edit: log_dynamic_columns in RequestBinder.py to increase this maximum authorized columns")


   def execQuery(self,query):
      logger.log("execQuery", Constants.DEBUG)
      cursor=self.connection.connect()
      if query.mode == "SELECT":
         logger.log(query.getQuery(), Constants.DEBUG)
         cursor.execute(query.getQuery())
	 # print columns names
         if query.isPrint:
  		 rows = cursor.fetchall()
         	 col_names = [tuple[0] for tuple in cursor.description]
		 logger.log("----------------------------------------------------------------------------",Constants.INFO)
		 if col_names:
			self.log_dynamic_columns(col_names,col_names)
		 logger.log("----------------------------------------------------------------------------",Constants.INFO)
		 # print rows 
	 	 for row in rows:
		    self.log_dynamic_columns(col_names, row)
	 else:
		return cursor
		
      else:
	 try:
		cursor.execute(query.getQuery())
	        self.connection.database.commit()
	        logger.log("Query executed", Constants.INFO)	
	 except sqlite3.IntegrityError, e:
		logger.log("Insertion Error: Integrity constraint not respected on pk or fk.", Constants.ERROR)

   def create(self,*table):
      cursor=self.connection.connect()
      tables = table
      for current_table in tables:
         logger.log(current_table.to_create_string(), Constants.DEBUG)
         cursor.execute(current_table.to_create_string())

   def executeQuery(self,query):
	logger.log(query, Constants.DEBUG)
	cursor=self.connection.connect()
	cursor.execute(query);

   def addFkConstraint(self,table,constraint_name,constraint_key, references_table, references_key):
	query = "ALTER TABLE " + table + " ADD CONSTRAINT " + constraint_name+" FOREIGN KEY("+constraint_key+") REFERENCES  "+references_table+"("+references_key+")"
	self.executeQuery(query)
	

class Request:
	def __init__(self, table_name):
		self.mode = "SELECT"
		self.table_name = table_name
		self.fields = []
		self.where_stmt = []	
 		self.values = list()
		self.isPrint = True

        def getTableName(self):
                return self.table_name

	def setMode(self, mode):
		self.mode = mode
		self.checkMode()
	
	def setIsPrint(self, isPrint):
		self.isPrint = isPrint

	def addValues(self, values):
		self.values.append("'" + values+"'")

	def addSelect(self, field):
		self.fields.append(str(field))

        def getSelect(self):
                return self.fields


	def addWhere(self, where_stmt):
		self.where_stmt.append(str(where_stmt))

	def checkMode(self):
		exists_modes = ["SELECT","INSERT","UPDATE","DELETE","CREATE"]
		if self.mode not in exists_modes:
			logger.log("Request "+ self.mode +"is not available on SQL", Constants.ERROR)

	def getQuery(self):
		fieldsStr = ""
		i=0
		if len(self.fields) > 0: 
			for selectField in self.fields:
				if i > 0:
					fieldsStr = fieldsStr +","+ str(selectField)
				else:
					fieldsStr = fieldsStr + str(selectField)
				i=i+1
		else:
			fieldsStr = "*"

		inserted_values = strutils.convert_list_to_str_insert(self.values)		

		if self.mode == "INSERT":	
			query = self.mode + " INTO " + self.table_name + " (" + fieldsStr + ") VALUES(" + inserted_values  + ")"
		elif self.mode == "DELETE":
                        query = self.mode + " FROM "+self.table_name
                else:
			query = self.mode + " " + fieldsStr + " FROM " + self.table_name
		
		where = ""
		for where_f in self.where_stmt:
			where = where + str(where_f)
		
		if where != "":
			query = query + " WHERE " +where
		return query


class Table:
	
	def __init__(self, table_name, *columns):
		self.name = table_name
		self.columns = columns
		self.constraint = ""

	def to_string_columns(self):
		columns =""
		i=0
		for column in self.columns:
			if i > 0:
				columns=columns+","+str(column)
			else:
				columns=str(column)
			
			i=i+1
		return columns

	def add_pk_constraint(self,constraint_name,constraint_key):
		self.constraint = self.constraint+ ", CONSTRAINT " + constraint_name+" PRIMARY KEY("+constraint_key+")"

	def add_fk_constraint(self,constraint_name,constraint_key, references_table, references_key):
		self.constraint = self.constraint+ ", CONSTRAINT " + constraint_name+" FOREIGN KEY("+constraint_key+") REFERENCES  "+references_table+"("+references_key+")"
	

	def to_create_string(self):
		query = '''CREATE TABLE '''+str(self.name)+'''('''+str(self.to_string_columns())
		if self.constraint != "":
			query = query + self.constraint
		query = query + ")"		
		return query
