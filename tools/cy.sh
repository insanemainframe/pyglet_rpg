#!/bin/sh

echo "CYTHON";
for i in $(find . -name '*.py');
	do
	f="${i%.*}";
	echo "$f"
	cp "$i" "$f.pyx"
	done