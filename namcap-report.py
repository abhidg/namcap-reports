#!/usr/bin/env python
# namcap-report: Generates pretty output of namcap.log

# Copyright (c) 2008, 2009 Abhishek Dasgupta <abhidg@gmail.com>
# Anyone may use this code for any purpose.
# There's no guarantee that this won't melt your computer
# or will not cause an apocalypse, etc. You get the idea.

ver="0.2"

import re, feedwriter, time, os, ConfigParser, sys
# Get the tag descriptions.
from tagscribe import tagscribe
from sys import exit

standard_locations=('/etc/namcap-reports.conf', 
	os.path.expanduser('~/.namcap-reports.conf'))

verbose=False
url, output_dir, template_dir, repo_files = "http://abhidg.mine.nu", "/arch", "/arch", "/arch"	

def warn(s):
	f = open(output_dir + '/namcap-report-error.log','a')
	print >>f, s
	if verbose: print >>sys.stderr, s

def die(s):
	print "E: "+s
	exit(1)

def tags(file):
	"Gets tag data from a file"

	if verbose: print "namcap-report: getting tag data from file..."	
	warnings = []
	errors = []
	tagd = {}

	try:
		f = open(file)
	except:
		die('Tags file could not be opened.')
	
	for i in f.readlines():
		m = re.match('. ([a-z,0-9,-]*) (.*)\n', i)
		type, tag, term = i[0],m.group(1), m.group(2)
		if type == 'W': warnings.append(tag)
		if type == 'E': errors.append(tag)
		tagd[tag] = term

	return warnings, errors, tagd

def tagname(line, tags):
	"Returns the tag code corresponding to a particular line."
	
	for i in tags.keys():
		if tags[i] in line: return i
		
def seelog(tags, logfile='namcap.log'):
	"Processes the log file."
	if verbose: print "namcap-report: processing the log file..."	
	pkglist = {}
	try:
		f = open(logfile)
	except:
		die('Log file could not be opened.')

	for i in f.readlines():
		m = re.match('.* \((.*)\).*\n',i)
		pkgname = m.group(1)
		if pkgname not in pkglist.keys():
			pkglist[pkgname] = []
		pkglist[pkgname].append(tagname(i, tags))

	return pkglist

def tagged(pkglist, tags):
	bytag = {}

	for t in tags.keys():
		for p in pkglist:
			if t in pkglist[p]:
				if t not in bytag.keys():
					bytag[t] = []
				bytag[t].append(p)
	return bytag

def repolist(repofiles):
	"""Returns a dictionary, in which the keys are the repository names,
	and the items are lists of packages in the particular repository.
	The input is a list of files (which itself must be named the *same*
	as the repository itself) in the current directory."""
	
	if verbose: print "namcap-report: making the repository list..."	

	repolist = {}
	# Assuming all the files are there, readable, etc. etc.
	for repo in repofiles:
		f = open(repo_files + "/" + repo)
		repolist[repo] = map(lambda s: s[:-1], f.readlines())
		f.close()

	return repolist

def repopkg(pkgname, repolist):
	"Returns the repository to which a particular package belongs."
	for repo in repolist:
		if pkgname in repolist[repo]:
			return repo
	warn("namcap-report: belongs-to-no-repository %s" % pkgname)
	return "none"

def tagclass(t, errors, warnings):
	if t in warnings: return 'W'
	if t in errors: return 'E'

def report(bytag, errors, warnings, tags, repos):

	if verbose: print "namcap-report: generating actual report..."	
	repodb = repolist(repos)
	f = open('index.html', 'w')
	last_updated=time.strftime('%d %b %Y %H:%M %z',time.gmtime(os.stat('namcap.log').st_mtime))

	progress_log = open(output_dir + '/namcap-report-progress.log', 'a')
	g = open(template_dir + '/index.html.tmpl')
	print >>f, ''.join(g.readlines()) % last_updated
	print >>f, "<ul>"
	for t in sorted(bytag.keys()):
		print >>f, """<li><span class="%s">%s</span><a href="tag/%s.html">%s</a> \
		  (%d packages)</li>""" % (tagclass(t, errors, warnings), \
          tagclass(t, errors, warnings), t, t, len(bytag[t]))

	print >>f, "</ul>"

	total_err = sum(map(lambda tag: tag in bytag.keys() and len(bytag[tag]) or 0,\
		filter(lambda t: t in errors, tags.keys())))
	total_warn = sum(map(lambda tag: tag in bytag.keys() and len(bytag[tag]) or 0,\
		filter(lambda t: t in warnings, tags.keys())))

	print >> progress_log, "%s\t%d\t%d" % (time.strftime('%Y%m%d', time.gmtime()), \
		total_err, total_warn)
	progress_log.close()

	progress_log_read = open(output_dir + '/namcap-report-progress.log')

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

	print >>f, "<p>namcap version: 2.2<br/>Design inspired by "\
		+ "<a href='http://lintian.debian.org'>lintian reports</a>.</p>"
	
	print >>f, "</body></html>"

	f.close()

	# Generate the tag pages.

	for t in bytag.keys():
		f = open('tag/'+t+'.html','w')
		print >>f, ''.join(open(template_dir + '/tags.html.tmpl').readlines()) % \
			(t, t, t, tagclass(t, errors, warnings), tagclass(t, errors, warnings) \
			, t, t, tagclass(t, errors, warnings), tagscribe.has_key(t) and \
			tagscribe[t] or "<p>"+tags[t]+"</p>", t)

		print >>f, "\n".join(map(lambda p: genlistitem(p, repodb), sorted(bytag[t])))
		print >>f, "</ul>"
		print >>f, "<hr/><p>Generated by <i>namcap-report</i> using " + \
			"<a href='../namcap.log'>namcap.log</a> of %s.</p></body></html>" % last_updated
		f.close()

def genlistitem(p, repodb):
	"Returns the <li> tag required in the display."
	repo_of_p = repopkg(p, repodb)
	if repo_of_p in ['core', 'extra']:
		return """<li class="%s">
<a href="http://archlinux.org/packages/%s/i686/%s/">%s</a>
<span class="%s">%s</span></li>"""	% (repo_of_p, repo_of_p, p, p, repo_of_p, repo_of_p)
	else:
		return """<li class="%s">%s <span class="%s">%s</span>
</li>""" % (repo_of_p, p, repo_of_p, repo_of_p)
	
def maint_report(maintainers, pkglist):
	"""Generates report by maintainer.
	maintainers: A dictionary in which the keys are the maintainers
	             and the items are lists of packages they maintain.
	pkglist:     Package listing comprising the tags, generated from
	             seelog(tags).
	"""
	pass

def rss(bytag, tags, repos):
	"Generates an RSS feed of the tags."
	repodb = repolist(repos)
	if verbose: print "namcap-report: generating the RSS feeds..."	
	last_updated_raw = os.stat('namcap.log').st_mtime
	head_url = url + "/tag/"
	package_url = "http://archlinux.org/packages/%s/i686/%s/"
	for t in bytag.keys():
		f = open('tag/'+t+'.rss','w')
		c = feedwriter.Channel(title='namcap tag: '+t, link=head_url+t, \
			description=(tagscribe.has_key(t) and tagscribe[t] or tags[t]))
		for pkg in sorted(bytag[t]):
			repo = repopkg(pkg, repodb)
			if repo in ['core', 'extra']:
				c.add_item(title=pkg, link=package_url % (repo, pkg), pubDate=last_updated_raw)
			else:
				c.add_item(title=pkg, pubDate=last_updated_raw)
		print >>f, c.rss2()
		f.close()

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
	
	# Remove any current error logs before starting the run
	config = ConfigParser.RawConfigParser()
	for location in standard_locations:
		numloc=0
		if os.path.exists(location):
			config.read(location)
			url=config.get('namcap-reports','url')
			output_dir=config.get('namcap-reports','output_dir')
			template_dir=config.get('namcap-reports','template_dir')
			repo_files=config.get('namcap-reports','repo_files')
			numloc+=1

	if numloc==0: die("No configuration file found\nPut a config file in either:" + \
		"\n  /etc/namcap-reports.conf\n  $HOME/.namcap-reports.conf")

	if os.path.exists(output_dir + '/namcap-report-error.log'):
		os.remove(output_dir + '/namcap-report-error.log')
	os.chdir(output_dir)
	warnings, errors, tags = tags('tags')
	pkglist = seelog(tags)
	bytag = tagged(pkglist, tags)
	report(bytag, errors, warnings, tags, ['core', 'extra', 'community'])
	rss(bytag, tags, ['core', 'extra', 'community'])
