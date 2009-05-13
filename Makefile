# Makefile for generating namcap-reports
# Abhishek Dasgupta 

DESTDIR=/
BINDIR=$(DESTDIR)/usr/bin/
CONFDIR=$(DESTDIR)/etc
MANDIR=$(DESTDIR)/usr/share/man
DOCDIR=$(DESTDIR)/usr/share/doc

default:
	# do nothing

install:
	install -D -m755 namcap-report.py $(BINDIR)/namcap-report
	install -D -m755 maintainer-report.py $(BINDIR)/maintainer-report
	mkdir -p $(DESTDIR)/usr/share/namcap-reports
	cp -R templates $(DESTDIR)/usr/share/namcap-reports/
	cp -R scripts $(DESTDIR)/usr/share/namcap-reports/
	install -D -m644 README $(DOCDIR)/namcap-reports/README
	install -D -m644 AUTHORS $(DOCDIR)/namcap-reports/AUTHORS
	install -D -m644 namcap-reports.conf $(CONFDIR)/namcap-reports.conf

