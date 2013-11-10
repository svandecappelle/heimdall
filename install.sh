#!/bin/bash
#
#
#This file is part of Heimdall.
#
#Heimdall is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#Heimdall is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with Heimdall.  If not, see <http://www.gnu.org/licenses/>. 
#
#Authors: 
#- Vandecappelle Steeve<svandecappelle@vekia.fr>
#- Sobczak Arnaud<asobczack@vekia.fr>
#
# Name:         install.sh
# Author:       Vandecappelle Steeve & Sobczak Arnaud
# Copyright:    (C) 2013-2014 Vandecappelle Steeve & Sobczak Arnaud
# Licence:      GNU General Public Licence version 3
# Website:      http://vekia.github.io/heimdall/
# Email:        svandecappelle at vekia.fr

# install heimdall dependencies
echo -e 'Installing Heimdall python RSA key replicator software under GNU General Public License.'
echo 

# python 2.7
echo -e 'Checking Python 2.7...'
python27=`dpkg -l | grep -E '^ii' | grep python2.7 | wc -l`
if [[ $python27 -eq 0 ]]
	then
			echo -e '\tpython 2.7 not installed. Installation...'
			sudo apt-get install python2.7
	else
			echo -e '\tpython 2.7 already installed. Nothing to do.'
fi

# python-paramiko==1.10
echo -e 'Checking python-paramiko...'
paramiko=`dpkg -l | grep -E '^ii' | grep python-paramiko | wc -l`
if [[ $paramiko -eq 0 ]]
	then
			echo -e '\tparamiko not installed. Installation...'
			sudo apt-get install python2.7-paramiko
	else
			echo -e '\tparamiko already installed. Nothing to do.'
fi

# postgresql
echo -e 'Checking postgresql...'
postgresql=`dpkg -l | grep -E '^ii' | grep postgresql | wc -l`
if [[ $postgresql -eq 0 ]]
	then
			echo -e '\tpostgresql not installed. Installation...'
			sudo apt-get install postgresql
	else
			echo -e '\tpostgresql already installed. Nothing to do.'
fi

# configure postgresql heimdall database
echo -e 'Checking Database...'
database=`sudo -u postgres psql -l | grep heimdall | wc -l`
if [[ $database -eq 0 ]]
	then
		echo -e "\tDatabase doesn't exist: creation..."
		echo -e '\tDatabase configuration...'
		read -s -p "\tEnter Password for heimdall database: " heimdallpasswd
		sudo -u postgres createdb heimdall
		sudo -u postgres createuser --no-createdb --no-createrole --no-superuser heimdall
		sudo -u postgres psql -U postgres -d postgres -c "alter user heimdall with password '"$heimdallpasswd"';"
		sed -i 's/$heimdallpasswd/'$heimdallpasswd'/g' server/server/settings.py
	else
		echo -e "\tDatabase already exists. Nothing to do."
fi

# python-psycopg2=2.4.5
echo -e 'Checking Python postgresql module...'
psycopg2=`dpkg -l | grep -E '^ii' | grep python-psycopg2 | wc -l`
if [[ $psycopg2 -eq 0 ]]
	then
			echo -e '\tpsycopg2 not installed. Installation...'
			sudo apt-get install python2.7-psycopg2
	else
			echo -e '\tpsycopg2 already installed. Nothing to do.'
fi

# WEB SERVER

# nginx=
echo -e 'Checking nginx...'
nginx=`dpkg -l | grep -E '^ii' | grep nginx | wc -l`
if [[ $nginx -eq 0 ]]
	then
			echo -e '\tnginx not installed. Installation...'
			sudo apt-get install nginx
	else
			echo -e '\tnginx already installed. Nothing to do.'
fi

echo -e 'Checking Python django... '
django=`dpkg -l | grep -E '^ii' | grep python-django | wc -l`
if [[ $django -eq 0 ]]
	then
			echo -e '\tdjango not installed. Installation...'
			sudo apt-get install python-django
	else
			echo -e '\tdjango already installed. Nothing to do.'
fi


echo -e 'Checking Python flup module for django... '
flup=`dpkg -l | grep -E '^ii' | grep python-flup | wc -l`
if [[ $flup -eq 0 ]]
	then
			echo -e '\tflup not installed. Installation...'
			sudo apt-get install python-flup
	else
			echo -e '\tflup already installed. Nothing to do.'
fi

echo 'Please enter webapp parameters: '
echo -e 'usage: let empty to default value [val]'
echo -ne "\t Server name:" 
read  servername
while [[ $servername = '' ]]
	do
		echo 'Incorrect server name retry with a non emty name'
		echo -ne "\tServer name: "
		read servername
done
webappport=80
echo -ne "\t Port [80]: "
read webappporttmp
if [[ $webappporttmp != '' ]]
	then
		webappport=$webappporttmp
fi
installdir=`pwd`
cgiport=8000
echo -ne "\t Port used to commnicate to python [8000]: "
read cgiporttmp
if [[ $cgiporttmp != '' ]]
	then
		cgiport=$cgiporttmp
fi

echo
echo 'Confirmation'
echo -e '\tServer name ' $servername
echo -e '\tPort ' $webbappport
echo -e '\tCGI Port ' $cgiport
echo -e '\tinstalldir ' $installdir 
echo

echo -ne 'Do you confirm the parameters, Y/n: '
read continue
echo 
if [[ $continue == 'y' || $continue == 'Y' ]]
	then
		installdir=`echo $installdir | tr '/' '\/'`
		cp .nginx-default.conf .nginx-heimdall.conf
		sed -i 's/$servername/'$servername'/g' .nginx-heimdall.conf
		sed -i 's/$webappport/'$webappport'/g' .nginx-heimdall.conf
		sed -i 's/$cgiport/'$cgiport'/g' .nginx-heimdall.conf
		sed -i 's;$installdir;'$installdir';g' .nginx-heimdall.conf


		sed -i 's/$servername/'$servername'/g' server/server/settings.py
		sed -i 's;$installdir;'$installdir';g' server/server/settings.py

		echo -e 'Installation finished.'
		echo -e 'You can now run the server using the run.sh script.'
		echo -e 'At first login you will invited to set an admin user and password in order to access to heimdall software.'
		echo -e 'Thank you for using it. If you have some problems or issue. Please report them to https://github.com/VekiaOpenSource/heimdall/issues'
	else 
		echo 'Cancelled'
fi

python2.7 server/manage.py syncdb