# Makefile for copying namcap-reports to the server
# Abhishek Dasgupta 

default:
	# do nothing	
fetch:
	abs # Run abs to get the latest stuff
	gen-namcap-log

report:
	cd ~/files/code/namcap-reports
	mv namcap.log namcap.old
	mv /var/abs/namcap.log .
	pacman -Sql community >| community
	pacman -Sql core >| core
	pacman -Sql extra >| extra
	python namcap-report.py

copy:
	backup namcap-reports

all: fetch report copy
	
