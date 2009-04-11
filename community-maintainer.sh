#!/bin/bash
# Author: Abhishek Dasgupta
# This script is in the public domain.

pkg=$1
if [ -z $pkg ]; then
	echo "Syntax: $0 pkgname"
	exit 1
fi
id=$(curl -s "http://aur.archlinux.org/rpc.php?type=info&arg=$pkg" \
	| sed "s#.*\"ID\":\"\([0-9]*\)\".*#\1#g")

curl -s http://aur.archlinux.org/packages.php?ID=$id | \
	grep "<span class='f3'>Maintainer:" | \
	sed "s#.*<span class='f3'>Maintainer: \(.*\)</span>.*#\1#g"
