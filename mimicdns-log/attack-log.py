import re
import os
import time
import datetime

log_path = '/var/log/syslog'        #syslog日志文件路径
#log_path = '/home/daniel/Desktop/syslog.txt'        #syslog日志文件路径



timedelta = 20

#日志时间字符串转换成时间戳
def time_shift(strtime):
    strtime = strtime + ' 2018'
    time_fmt = '%b  %d %H:%M:%S %Y'
    ptime = datetime.datetime.strptime(strtime,time_fmt)
    return ptime.timestamp()

#返回timedelta分钟前的时间戳
def delta_minute():
    a = (datetime.datetime.today()-datetime.timedelta(minutes=timedelta)).timestamp()
    return a

def logfilename():
    easytime = time.strftime('%Y%m%d%H%M',time.localtime())
    file_name = 'dns_attack_%s.log' %easytime
    return file_name


def time_extract(line):
    l = line.split()[:3]
    log_time = l[0]+'  '+l[1]+' '+l[2]
    return log_time

def ip_extract(line):
    reip = re.compile("(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])")   #匹配IP地址的正则表达式
    ip = reip.findall(line)
    if(len(ip)):
        return ip[0]
    else:
        return None


def syslog_process(log_path,exam_minute):

    step = 1000
    # open log file to write IP
    try:
        dest_log = logfilename()
        fd_destlog = open(dest_log,'w')
    except:
        print('dest log file open failed!\n')
    #open syslog file
    try:
        fd_syslog = open(log_path)
        line = fd_syslog.readline()
        #尽快找到时间合适的地方
        while line:
            logtime = time_shift(time_extract(line))
            #print('logtime:',logtime)
            #print('examtime:',exam_minute)
            if logtime >= exam_minute:
                fd_syslog.seek(fd_syslog.tell()-step)
                fd_syslog.readline()       #将该行读完         
                break
            fd_syslog.seek(fd_syslog.tell()+step)
            #超过文件大小，则向前
            if fd_syslog.tell()>=os.path.getsize(log_path):
                fd_syslog.seek(fd_syslog.tell()-step)
                fd_syslog.readline()
                break
            fd_syslog.readline()
            line = fd_syslog.readline()
        #顺序查找时间正确的行
        for line in fd_syslog:
            #print(line)
            logtime = time_shift(time_extract(line))
            if logtime >= exam_minute:
                ip = ip_extract(line)
                if(ip):
                    print('Writing IP to log...\n')
                    fd_destlog.write(ip+'\n')
            else:
                continue
    except Exception as e:
        print('error!',e)
    finally:
        fd_destlog.close()
        fd_syslog.close()


if __name__ == '__main__':
    delta_min = delta_minute()
    syslog_process(log_path, delta_min)