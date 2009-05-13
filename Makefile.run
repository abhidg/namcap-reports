# Makefile for generating namcap-reports
# Abhishek Dasgupta 

WORKDIR=/arch

default:
	# do nothing	
fetch:
	/usr/bin/abs # Run abs to get the latest stuff
	${WORKDIR}/gen-namcap-log

report:
	/bin/mv ${WORKDIR}/namcap.log ${WORKDIR}/namcap.old || /bin/echo "W: No old namcap.log found."
	/bin/mv /var/abs/namcap.log ${WORKDIR}
	${WORKDIR}/gen-pkglist-by-repository
	/opt/local/bin/python2.5 ${WORKDIR}/namcap-report.py

maintainers:
	${WORKDIR}/generate-maintainer-list
	/opt/local/bin/python2.5 ${WORKDIR}/maintainer-report.py

all: fetch report maintainers
	
