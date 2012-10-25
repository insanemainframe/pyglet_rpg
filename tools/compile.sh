#!/bin/sh

echo "CYTHON";
for i in $(find . -name '*.pyx');
	do
	f="${i%.*}";
	echo "$f"
	cython "$f.pyx"
	done

echo "GCC";

for i in $(find . -name '*.c');
	do
	f="${i%.*}";
	echo "$f"
	gcc -c -fPIC -I /usr/include/python2.7 "$f.c" -o "$f.o";
	done

echo "COMPILE";

for i in $(find . -name '*.o');
	do
	f="${i%.*}";
	echo "$f"
	gcc -shared "$f.o" -o "$f.so";
	done

