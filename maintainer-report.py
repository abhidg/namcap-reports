#!/opt/local/bin/python2.5
# -*- coding: utf-8 -*-

# Copyright (c) 2009, Abhishek Dasgupta <abhidg@gmail.com>
# Anyone may use this code for any purpose.
# There's no guarantee that this won't melt your computer
# or will not cause an apocalypse, etc. You get the idea.

ver="0.2"
import re, sys, time, os, ConfigParser
from maintainers import maintainers

verbose=False

standard_locations = ('/etc/namcap-reports.conf', \
	os.path.expanduser('~/.namcap-reports.conf'))

def warn(s):
	f = open(output_dir + '/maintainer-report-error.log','a')
	print >>f, s
	if verbose: print >>sys.stderr, s

def parse_maintainer(m):
	"Parses the Maintainer string"
	if "Maintainer" not in m: return "nobody"
	r = re.match('.*Maintainer\s*:(.*)<.*', m)
	try:
		name = r.group(1).strip()
	except:
		return "error"

	if name not in maintainers.keys():
		warn("maintainer-report: not-a-maintainer " + name)
		return "someone"
	else:
		return maintainers[name]

def getname(id):
	if id == "error": return "Error in Maintainer"
	if id == "nobody" : return "Orphans"
	if id == "someone" : return "Somebody"

	for m in maintainers.keys():
		if maintainers[m] == id and m[0].isupper(): return m

def parse_namcap(filename='namcap.log'):
	f = open(filename)
	namcaplist = {}
	for i in f.readlines():
		r = re.match('PKGBUILD \((.*)\)\s*([WEI]: .*)',i[:-1])
		if r.group(1) not in namcaplist.keys():
			namcaplist[r.group(1)] = []
		namcaplist[r.group(1)].append(r.group(2))
	return namcaplist

def print_namcap(thing):
	return "<li><span class='%s'>%s</span> %s</li>" % (thing[0], thing[0], thing[3:])

def version():
	print "maintainer-report " + ver
	print "This is an utility to generate reports by maintainer from"
	print "the namcap output after running namcap over a set of PKGBUILDs."
	print "namcap is part of the Archlinux distribution (archlinux.org)"
	print
	print "Copyright (C) 2008, 2009 Abhishek Dasgupta <abhidg@gmail.com>"
	print "Check the COPYING file for license details."

if __name__ == "__main__":
	if "--version" in sys.argv:
		version()
		sys.exit(0)

	if "-v" in sys.argv or "--verbose" in sys.argv: verbose=True
	config = ConfigParser.RawConfigParser()
	for location in standard_locations:
		numloc=0
		if os.path.exists(location):
			config.read(location)
			output_dir=config.get('namcap-reports','output_dir')
			template_dir=config.get('namcap-reports','template_dir')
			repo_files=config.get('namcap-reports','repo_files')
			numloc+=1

	if numloc==0: die("No configuration file found\nPut a config file in either:" + \
		"\n  /etc/namcap-reports.conf\n  $HOME/.namcap-reports.conf")
	
	
	if os.path.exists(output_dir + '/maintainer-report-error.log'):
		os.remove(output_dir + '/maintainer-report-error.log')
	
	# Beginning of main code.
	f = open(repo_files + "/maintainers.txt")
	maintpkg = {}
	for i in f.readlines():
		id, pkg = i[:-1].split(",")
		id = parse_maintainer(id)
		pkg = pkg.strip()
		if id not in maintpkg.keys():
			maintpkg[id] = []
		maintpkg[id].append(pkg)
	
	f.close()
	last_updated=time.strftime('%d %b %Y %H:%M %z',time.gmtime(os.stat(output_dir\
		+ '/namcap.log').st_mtime))
	f = open(template_dir + '/maintainer.index.html.tmpl')
	g = open(output_dir + '/maintainer/index.html','w')
	print >>g, ''.join(f.readlines()) % last_updated
	f.close()
	print >>g, "<ul>"
	namcaplist = parse_namcap(output_dir + '/namcap.log')
	maintainer_ids = maintpkg.keys()
	maintainer_ids.sort(key=getname)
	for id in maintainer_ids:
		h = open(output_dir + '/maintainer/' + id + '.html', 'w')
		f = open(template_dir + '/maintainer.html.tmpl')
		print >>h, ''.join(f.readlines()) % (getname(id), getname(id), id, getname(id))
		for pkg in sorted(maintpkg[id]):
			if pkg in namcaplist:
				print >>h, "<h2>%s</h2> <ul>" % pkg
				for thing in namcaplist[pkg]: print >>h, print_namcap(thing)
				print >>h, "</ul>"
		print >>g, "<li><a href='%s'>%s (%s)</a></li>" % (id, getname(id), id)
		print >>h, "</body></html>"
		h.close()

	print >>g, "</ul></body></html>"
	
