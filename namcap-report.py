#!/usr/bin/env python
# namcap-report: Generates pretty output of namcap.log

# Copyright (c) 2008, 2009 Abhishek Dasgupta <abhidg@gmail.com>
# Anyone may use this code for any purpose.
# There's no guarantee that this won't melt your computer
# or will not cause an apocalypse, etc. You get the idea.

ver="0.2.91"

import re
import time
import os
import ConfigParser
import sys
import operator

# Get the tag descriptions.
from sys import exit

standard_locations=('/etc/namcap-reports.conf', 
	os.path.expanduser('~/.namcap-reports.conf'))

verbose=False

# Defaults
url = "http://abhidg.mine.nu"
output_dir = ""
template_dir = "/usr/share/namcap-reports/templates"
log_dir = "log"
repo_files = "repository"

def warn(s):
	if not os.path.exists(log_dir):
		os.mkdir(log_dir)
	f = open(os.path.join(log_dir, 'namcap-report-error.log'),'a')
	print >>f, s
	if verbose: print >>sys.stderr, s

def die(s):
	print "E: "+s
	exit(1)

def tagname(line, tags):
	"Returns the tag code corresponding to a particular line."
	
	for i in tags.keys():
		if tags[i] in line: return i
		
def seelog(logfile='namcap.log'):
	"Processes the log file and sorts packages into tags."
	if verbose: print "namcap-report: processing the log file..."	

	tags = {}
	sourcere = 'PKGBUILD \((.*)\)\s+([W,E]: .*)'
	packagere = '(.*)\s+([W,E]: .*)'
	pkglist = {}
	try:
		f = open(logfile)
	except:
		die('Log file could not be opened.')

	for i in f.readlines():
		if i.startswith('PKGBUILD'):
			m = re.match(sourcere, i)
			source=True
		else:
			source=False
			m = re.match(packagere, i)
		pkgname = m.group(1)
		if source: pkgname += " (source)"
		tagplusinfo = m.group(2)
		tagdata = ""
		try:
			tagm = re.match("([W,E]: \S+) (.*)", tagplusinfo)
			tagdata = tagm.group(2).strip()
			tag = tagm.group(1)
		except:
			tag = tagplusinfo.strip()

		if tag not in tags.keys():
			tags[tag] = {}
		if pkgname not in tags[tag]:
			tags[tag][pkgname] = []
		if tagdata != "":
			tags[tag][pkgname].append(tagdata)
			
	return tags

def repolist(repofiles):
	"""Returns a dictionary, in which the keys are the repository names,
	and the items are lists of packages in the particular repository.
	The input is a list of files (which itself must be named the *same*
	as the repository itself) in the current directory."""
	
	if verbose: print "namcap-report: making the repository list..."	

	repolist = {}
	# Assuming all the files are there, readable, etc. etc.
	for repo in repofiles:
		f = open(os.path.join(repo_files, repo))
		repolist[repo] = map(lambda s: s[:-1], f.readlines())
		f.close()

	return repolist

def repopkg(pkgname, repolist):
	"Returns the repository to which a particular package belongs."
	pkgname = pkgname.strip()
	for repo in repolist:
		if pkgname in repolist[repo]:
			return repo
	warn("namcap-report: belongs-to-no-repository %s" % pkgname)
	return "none"

def report(tags, repos):

	if verbose: print "namcap-report: generating actual report..."	
	repodb = repolist(repos)

	total_warn = 0
	total_err = 0

#	tags is obtained from seelog(), see above.
	taglist = tags.keys()
#	strips W,E: from the front of the tag and then sorts.
	taglist.sort(key=operator.itemgetter(slice(3, None)))

	f = open('index.html', 'w')
	last_updated=time.strftime('%d %b %Y %H:%M %z',time.gmtime(os.stat('namcap.log').st_mtime))

	progress_log = open(os.path.join(output_dir, 'namcap-report-progress.log'), 'a')
	g = open(os.path.join(template_dir, 'index.html.tmpl'))
	print >>f, ''.join(g.readlines()) % last_updated
	g.close()
	print >>f, "<ul>"
	for t in taglist:
		print >>f, "<li><span class='%s'>%s</span><a href='tag/%s.html'>%s</a>" \
				" (%d package%s)</li>" % (t[0], t[0], t[3:], t[3:], len(tags[t]), \
				len(tags[t]) > 1 and "s" or "")

	print >>f, "</ul>"

	for tag in taglist:
		ntag = 0
		taghasdata = True
		for pkg in tags[tag].keys():
			if tags[tag][pkg] == []: taghasdata = False
			if not taghasdata:
				ntag += len(tags[tag])
				break
			else:
				ntag += len(tags[tag][pkg])
		if tag[0] == "W": total_warn += ntag
		if tag[0] == "E": total_err += ntag

	print >> progress_log, "%s\t%d\t%d" % (time.strftime('%Y%m%d', time.gmtime()), \
		total_err, total_warn)
	progress_log.close()

	progress_log_read = open(os.path.join(output_dir, 'namcap-report-progress.log'))

	# Process the last fortnight's data and generate a sparkline.
	error_history, warning_history = [], []
	for i in progress_log_read.readlines()[-30:]:
		progress_log_fields = i[:-1].split()
		error_history.append(int(progress_log_fields[1]))
		warning_history.append(int(progress_log_fields[2]))

	try:
		lasterr, lastwarn = error_history[-2], warning_history[-2]
	except:
		lasterr, lastwarn = 0, 0
	
	print >>f, """
<p>Total number of errors: %d (%d)
<img src="http://sparklines-bitworking.appspot.com/spark.cgi?type=impulse&d=%s&limits=%d,%d&height=12&above-color=red"
alt="error sparkline" /> (<a href="namcap-report-progress.log">progress</a>)<br/>
Total number of warnings: %d (%d)
<img src="http://sparklines-bitworking.appspot.com/spark.cgi?type=impulse&d=%s&limits=%d,%d&height=12&above-color=orange"
alt="warning sparkline" />
</p> """ % (total_err, total_err-lasterr, ",".join(map(lambda s: str(s), error_history)), \
		min(error_history), max(error_history), \
		total_warn, total_warn-lastwarn, ",".join(map(lambda s: str(s), warning_history)), \
		min(warning_history), max(warning_history))

	print >>f, """
<p class="footer">namcap version: <b>2.2</b> design inspired by
<a href='http://lintian.debian.org'>lintian reports</a>.<br/>
sparklines generated using <a href='http://sparklines-bitworking.appspot.com'>
http://sparklines-bitworking.appspot.com</a></p>"""
	
	print >>f, "</body></html>"

	f.close()

	# Generate the tag pages.
	if not os.path.exists("tag"):
		os.mkdir("tag")

	for t in taglist:
		taghasdata = True
		f = open(os.path.join('tag', t[3:]+'.html'),'w')
		g = open(os.path.join('tag', t[3:]+'.txt'),'w')
		tagheader = ''.join(open(os.path.join(template_dir, 'tags.html.tmpl')).readlines())
		tagheader = tagheader.replace("%tagclass%", t[0])
		tagheader = tagheader.replace("%tag%", t[3:])
		tagheader = tagheader.replace("%pkgplural%", len(tags[t].keys()) > 1 and
				"packages have" or "package has")

		print >>f, tagheader
		print >>g, "Tag: " + t[3:]
		print >>g, "Generated: " + last_updated
		print >>g

		pkgs = tags[t].keys()
		pkgs.sort()
		if tags[t][pkgs[0]] == []: taghasdata = False
	
		print >>f, "<ul>"
		if not taghasdata:
			print >>f, '\n'.join(map(lambda p: genlistitem(p, repodb), pkgs))
			print >>g, '\n'.join(map(lambda p: repopkg(p.endswith("(source)") \
					and p[:-9] or p, repodb) + "/" + p, pkgs))
		else:
			for p in pkgs:
				print >>f, genlistitem(p, repodb)[:-5]
				print >>g, repopkg(p, repodb) + "/" + p
				print >>f, "<ul>"
				for item in tags[t][p]:
					print >>f, "<li>" + item + "</li>"
					print >>g, "  " + item
				print >>f, "</ul></li>"
		
		print >>f, "</ul>"
		print >>f, "<hr/><p>Generated by <i>namcap-report</i> using " + \
			"<a href='../namcap.log'>namcap.log</a> of %s.</p></body></html>" % last_updated
		f.close()
		g.close()

def genlistitem(p, repodb):
	"Returns the <li> tag required in the display."
	pkg = p
	sourcetag = ""
	if p.endswith("(source)"):
		pkg = p[:-9]
		sourcetag = " <span class='src'>(source)</span>"
	repo_of_p = repopkg(pkg, repodb)
	if repo_of_p in ['core', 'extra']:
		return """<li class="%s">
<a href="http://archlinux.org/packages/%s/i686/%s/">%s</a>
%s<span class="%s">%s</span></li>"""	% (repo_of_p, repo_of_p, pkg.strip(), pkg.strip(), sourcetag, repo_of_p, repo_of_p)
	else:
		return """<li class="%s">%s%s<span class="%s">%s</span>
</li>""" % (repo_of_p, pkg, sourcetag, repo_of_p, repo_of_p)
	
def version():
	print "namcap-reports " + ver
	print "This is an utility to generate reports from the namcap"
	print "output after running namcap over a set of PKGBUILDs."
	print "namcap is part of the Archlinux distribution (archlinux.org)"
	print
	print "Copyright (C) 2008, 2009 Abhishek Dasgupta <abhidg@gmail.com>"
	print "Check the COPYING file for license details."

if __name__ == "__main__":
	if "--version" in sys.argv:
		version()
		exit(1)
	if "-v" in sys.argv or "--verbose" in sys.argv: verbose=True
	
	numloc=0
	config = ConfigParser.SafeConfigParser({
		'url': url,
		'template_dir': template_dir,
		'output_dir': output_dir,
		'repo_files': repo_files,
		})
	for location in standard_locations:
		if os.path.exists(location):
			config.read(location)
			url=config.get('namcap-reports','url')
			output_dir=config.get('namcap-reports','output_dir')
			template_dir=config.get('namcap-reports','template_dir')
			repo_files=config.get('namcap-reports','repo_files')
			numloc+=1

	if numloc==0: die("No configuration file found\nPut a config file in either:" + \
		"\n  /etc/namcap-reports.conf\n  $HOME/.namcap-reports.conf")

	# Remove any current error logs before starting the run
	if os.path.exists(os.path.join(output_dir, 'namcap-report-error.log')):
		os.remove(os.path.join(output_dir, 'namcap-report-error.log'))
	os.chdir(output_dir)
	tags = seelog()
	report(tags, ['core', 'extra', 'community'])
