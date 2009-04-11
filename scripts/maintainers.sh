#!/bin/sh
# Generate a list of packages and maintainers.

ROOT=/var/abs

for i in $(find $ROOT | grep PKGBUILD); do
	source $i
	echo "$(basename $(dirname $i)), $(grep Maintainer $i | head -n 1)"
done
