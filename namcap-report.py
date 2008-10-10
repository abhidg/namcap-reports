#!/usr/bin/env python
# namcap-report: Generates pretty output of namcap.log

# Written by Abhishek Dasgupta <abhidg@gmail.com>
# feedparser.py from http://offog.org/code/misccode.html

import re, feedwriter, time
from sys import exit

def die(s):
	print "E: "+s
	exit(1)

def tags(file):
	"Gets tag data from a file"
	
	warnings = []
	errors = []
	tagdescs = {}

	try:
		f = open(file)
	except:
		die('Tags file could not be opened.')
	
	for i in f.readlines():
		m = re.match('. ([a-z,0-9,-]*) (.*)\n', i)
		type, tag, term = i[0],m.group(1), m.group(2)
		if type == 'W': warnings.append(tag)
		if type == 'E': errors.append(tag)
		tagdescs[tag] = term

	return warnings, errors, tagdescs

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

def tagclass(t, errors, warnings):
	if t in warnings: return 'W'
	if t in errors: return 'E'

def report(bytag, errors, warnings, tags):
	f = open('index.html', 'w')

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
after running namcap against the <tt>community</tt> tree.</p>
<p>You can get the <a href="namcap.log">namcap.log</a> from which
this report was generated.</p>
"""
	print >>f, "<ul>"
	for t in sorted(bytag.keys()):
		print >>f, """<li><span class="%s">%s</span><a href="tag/%s">%s</a> (%d packages)</li>""" % (tagclass(t, errors, warnings), tagclass(t, errors, warnings), t, t, len(bytag[t]))
	print >>f, "</ul>"

	print >>f, "<p>Total number of errors: %s<br/>Total number of warnings: %s</p>" % ( \
		sum(map(lambda tag: tag in bytag.keys() and len(bytag[tag]) or 0,\
		filter(lambda t: t in errors, tags.keys()))), \
		sum(map(lambda tag: tag in bytag.keys() and len(bytag[tag]) or 0,\
		filter(lambda t: t in warnings, tags.keys()))))

	print >>f, "<p>namcap version: 2.1<br/>Design inspired by <a href='http://lintian.debian.org'>lintian reports</a>.</p>"
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
</head>
<body>
<h1><span class="%s">%s</span>%s</h1>
<p>The list of all the tags can be found <a href="..">here</a>.<br/>
The following packages have the namcap tag: %s<br/>The description of this tag is:</p>
<p>%s</p>
<p>An <a href="%s.rss">RSS</a> feed is available for this page.</p>
""" % (t, t, t, tagclass(t, errors, warnings), tagclass(t, errors, warnings), t, t, tags[t], t)
		print >>f, "\n".join(map(lambda p: "<li>"+p+"</li>", sorted(bytag[t])))
		print >>f, "</ul></body></html>"
		f.close()

def rss(bytag, tags):
	"Generates an RSS feed of the tags."
	head_url = "http://abhidg.mine.nu/arch/namcap-reports/tag/"
	for t in bytag.keys():
		f = open('tag/'+t+'.rss','w')
		c = feedwriter.Channel(title='namcap tag: '+t, link=head_url+t, description=tags[t])
		for pkg in sorted(bytag[t]): c.add_item(title=pkg, link=head_url+t, pubDate=time.time())
		print >>f, c.rss2()
		f.close()
	
if __name__ == "__main__":
	warnings, errors, tags = tags('tags')
	bytag = tagged(seelog(tags), tags)
	report(bytag, errors, warnings, tags)
	rss(bytag, tags)




