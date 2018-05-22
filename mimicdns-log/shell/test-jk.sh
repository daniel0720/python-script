#!/bin/sh

while [ 1 ]
do
problem_date=`date '+%Y-%m-%d %H:%M:%S'`
problem_file=`date '+%Y-%m-%d-%H:%M:%S'`
snort=`ps -ef|grep "snort -s -q"|grep -v grep|wc -l|awk '{print $1"\n"}'`
#access-dump=`ps -ef|grep "access-dump.py"|grep -v grep|wc -l|awk '{print $1"\n"}'`
#attack-log=`ps -ef|grep "attack-log.py"|grep -v grep|wc -l|awk '{print $1"\n"}'`
tcpdump=`ps -ef|grep "tcpdump -i p6p3 dst"|grep -v grep|grep -v "dump0510.pcap"|wc -l|awk '{print $1"\n"}'`
tcpdump1=`ps -ef|grep "dump0510.pcap"|grep -v grep|wc -l|awk '{print $1"\n"}'`

	if [ $snort = 0 ]
	then
	printf "$problem_date snort Restart!\n" >> /home/daniel/JK.log
	/usr/local/bin/snort -s -q -i p6p3 -c /etc/snort/snort.conf&
	fi

	if [ $tcpdump = 0 ]
	then
	printf "$problem_date tcpdump Restart!\n" >> /home/daniel/JK.log
	/usr/sbin/tcpdump -i p6p3 dst host 172.29.4.66 >/home/daniel/cachedns.txt& 
	fi

	if [ $tcpdump1 = 0 ]
	then
	printf "$problem_date tcpdump1 Restart!\n" >> /home/daniel/JK.log
	/usr/sbin/tcpdump -i p6p3 dst host 172.29.4.66 -C 1 -w /home/daniel/dump0510.pcap& 
	fi
sleep 60
done
