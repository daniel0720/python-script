#!/bin/sh

while [ 1 ]
do
problem_date=`date '+%Y-%m-%d %H:%M:%S'`
problem_file=`date '+%Y-%m-%d-%H:%M:%S'`
access=`ps -ef|grep "access-dump.py"|grep -v grep|wc -l|awk '{print $1"\n"}'`
attack=`ps -ef|grep "attack-log.py"|grep -v grep|wc -l|awk '{print $1"\n"}'`

        if [ $access = 0 ]
        then
        printf "$problem_date snort Restart!\n" >> /home/daniel/JK.log
        /usr/bin/python3.4 /home/daniel/access-dump.py > /home/daniel/access.log &
        fi

        if [ $attack = 0 ]
        then
        printf "$problem_date attack-log Restart!\n" >> /home/daniel/JK.log
	/usr/bin/python3.4 /home/daniel/attack-log.py > /home/daniel/attack.log &
        fi
sleep 60
done
