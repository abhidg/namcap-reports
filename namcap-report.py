#!/usr/bin/env python
# namcap-report: Generates pretty output of namcap.log

# Written by Abhishek Dasgupta <abhidg@gmail.com>
# feedparser.py from http://offog.org/code/misccode.html

import re, feedwriter, time, os
# Get the tag descriptions.
from tagscribe import tagscribe
from sys import exit

def die(s):
	print "E: "+s
	exit(1)

def tags(file):
	"Gets tag data from a file"
	
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

	repolist = {}
	# Assuming all the files are there, readable, etc. etc.
	for repo in repofiles:
		f = open(repo)
		repolist[repo] = map(lambda s: s[:-1], f.readlines())
		f.close()

	return repolist

def repopkg(pkgname, repolist):
	"Returns the repository to which a particular package belongs."
	for repo in repolist:
		if pkgname in repolist[repo]:
			return repo
	print "E: %s belongs to no repository!" % pkgname
	return "none"

def tagclass(t, errors, warnings):
	if t in warnings: return 'W'
	if t in errors: return 'E'

def report(bytag, errors, warnings, tags, repos):
	repodb = repolist(repos)
	f = open('index.html', 'w')
	last_updated=time.strftime('%d %b %Y %H:%M %z',time.gmtime(os.stat('namcap.log').st_mtime))

	print >>f, """
<html>
<head>
<title>namcap reports</title>
<link rel="stylesheet" type="text/css" href="/arch/arch.css" />
</head>
<body>
<h1>namcap reports</h1>
<p>
namcap is a utility for <a href="http://archlinux.org">Archlinux</a>
which helps in automatic detection of common mistakes and errors in
PKGBUILDs. This page is an automatically generated report obtained
after running namcap against the <tt>core</tt>, <tt>extra</tt> and
<tt>community</tt> trees.</p>
<p>You can get the <a href="namcap.log">namcap.log</a> from which
this report was generated.<br/>
(last generated on <span class="date">%s</span>)</p>
<p>The code can be found in <a href="/gitweb">gitweb</a>.</p>
""" % last_updated
	print >>f, "<ul>"
	for t in sorted(bytag.keys()):
		print >>f, """<li><span class="%s">%s</span><a href="tag/%s">%s</a> (%d packages)</li>""" % (tagclass(t, errors, warnings), tagclass(t, errors, warnings), t, t, len(bytag[t]))
	print >>f, "</ul>"

	print >>f, "<p>Total number of errors: %s<br/>Total number of warnings: %s</p>" % ( \
		sum(map(lambda tag: tag in bytag.keys() and len(bytag[tag]) or 0,\
		filter(lambda t: t in errors, tags.keys()))), \
		sum(map(lambda tag: tag in bytag.keys() and len(bytag[tag]) or 0,\
		filter(lambda t: t in warnings, tags.keys()))))

	print >>f, "<p>namcap version: 2.2<br/>Design inspired by <a href='http://lintian.debian.org'>lintian reports</a>.</p>"
	print >>f, "</body></html>"
	f.close()

	# Generate the tag pages.

	for t in bytag.keys():
		f = open('tag/'+t+'.html','w')
		print >>f, """<html>
<head>
<title>namcap tag: %s</title>
<link rel="stylesheet" type="text/css" href="/arch/arch.css" />
<link rel="alternate" type="application/rss+xml" title="namcap tag: %s" href="http://abhidg.mine.nu/arch/namcap-reports/tag/%s.rss" />
<script type="text/javascript" src="/jquery-1.2.6.min.js"></script>
<script type="text/javascript" src="../togglers.js"></script>
</head>
<body>
<h1><span class="%s">%s</span>%s</h1>
<p>The list of all the tags can be found <a href="..">here</a>.<br/>
The following packages have the namcap tag: %s<br/>The description of this tag is:</p>
<div class="%s">
%s
</div>
<p><img src="/i/feed-icon-14x14.png" alt="RSS" /> An <a href="%s.rss">RSS</a> feed is available for this page.<br/>
toggle <a href="#" id="toggle-core">core</a> <a href="#" id="toggle-extra">extra</a>
<a href="#" id="toggle-community">community</a></p>
""" % (t, t, t, tagclass(t, errors, warnings), tagclass(t, errors, warnings), t, t, tagclass(t, errors, warnings), tagscribe.has_key(t) and tagscribe[t] or "<p>"+tags[t]+"</p>", t)
		print >>f, "\n".join(map(lambda p: genlistitem(p, repodb), sorted(bytag[t])))
		print >>f, "</ul>"
		print >>f, "<hr/><p>Generated by <i>namcap-report</i> using <a href='../namcap.log'>namcap.log</a> of %s.</p></body></html>" % last_updated
		f.close()

def genlistitem(p, repodb):
	"Returns the <li> tag required in the display."
	repo_of_p = repopkg(p, repodb)
	return "<li class='"+repo_of_p +"'>"+p+" <span class='"+repo_of_p+"'>"+repo_of_p+"</span></li>"
	
def maints(repo):
	"Creates a dictionary of maintainers: packages by parsing repo."
#	for xome in os..walk(repo)

def maint_report(maintainers, pkglist):
	"""Generates report by maintainer.
	maintainers: A dictionary in which the keys are the maintainers
	             and the items are lists of packages they maintain.
	pkglist:     Package listing comprising the tags, generated from
	             seelog(tags).
	"""
	pass

def rss(bytag, tags):
	"Generates an RSS feed of the tags."
	last_updated_raw = os.stat('namcap.log').st_mtime
	head_url = "http://abhidg.mine.nu/arch/namcap-reports/tag/"
	for t in bytag.keys():
		f = open('tag/'+t+'.rss','w')
		c = feedwriter.Channel(title='namcap tag: '+t, link=head_url+t, description=(tagscribe.has_key(t) and tagscribe[t] or tags[t]))
		for pkg in sorted(bytag[t]): c.add_item(title=pkg, link=head_url+t, pubDate=last_updated_raw)
		print >>f, c.rss2()
		f.close()
	
if __name__ == "__main__":
	warnings, errors, tags = tags('tags')
	pkglist = seelog(tags)
	bytag = tagged(pkglist, tags)
	report(bytag, errors, warnings, tags, ['core', 'extra', 'community'])
	rss(bytag, tags)
	#maint_report(maintainers, pkglist)
