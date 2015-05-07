#!/bin/bash

username=
password=

cat ./source/group_list.txt | \
while read line
do
	echo -e "\n\n\n $line"
	python fb-crawler.py -username $username -password $password -query member -group $line

    pids=$(pidof /usr/bin/Xvfb)
	echo "Xvfb pids : $pids"
	kill $pids
	ps
done