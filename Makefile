# Makefile for generating namcap-reports
# Abhishek Dasgupta 

DESTDIR=/usr
CONFDIR=/etc

default:
	# do nothing

install:
	install -D -m755 namcap-report.py $(DESTDIR)/bin/namcap-report
	install -D -m755 maintainer-report.py $(DESTDIR)/bin/maintainer-report
	install -D templates $(DESTDIR)/share/namcap-reports/
	install -D scripts $(DESTDIR)/share/namcap-reports/
	install -D -m644 README $(DESTDIR)/share/doc/namcap-reports/README
	install -D -m644 AUTHORS $(DESTDIR)/share/doc/namcap-reports/AUTHORS
	install -D -m644 namcap-reports.conf $(CONFDIR)/namcap-reports.conf

