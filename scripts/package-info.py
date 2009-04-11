#!/usr/bin/env python
# Retrieves AUR package information and stores
# it in the form of a dictionary.

import urllib, pickle

def info(package):
	"Returns a dictionary of information about the package"
	url = "http://aur.archlinux.org/rpc.php?type=info&arg=" + package
	d = eval(urllib.urlopen(url).read())
	return d["results"]

def getpkgnames(file="community-packages.txt"):
	"Returns package names from a txt file."

	f = open(file)
	return sorted(map(lambda s: s[:-1], f.readlines()))

def pkgdb(pkgnames):
	"Prepare a database (dictionary) of package information."
	d = {}
	for pkg in pkgnames: d[pkg] = info(pkg)
	return d

if __name__ == "__main__":
	d = pkgdb(getpkgnames())
	pickle.dump(d, open('pkg.db','wb'))
	




