import re
import os
import time
import datetime

log_path = '/var/log/auth.log'        #syslog日志文件路径
# log_path = '/home/daniel/Desktop/syslog.txt'        #syslog日志文件路径
timedelta = 1
destlog_path = '/home/daniel/log/'

# 日志时间字符串转换成时间戳
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

def netcheck():
    try:
        now = time.asctime(time.localtime(time.time()))
        ret = os.system('ping 172.29.91.109 -c 1 -w 1')
        #ret = subprocess.Popen(['ping 172.29.91.109 -c 1 -w 1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        #out = ret.stdout.read()
        #out = out.decode('utf-8')
        #regex = re.compile('100% packet loss')
        #if len(regex.findall(out)) == 0:
        if ret:
            print(now, "Network is unreachable!!!")
            #print(now, 'Network is OK!!!')
            #return 'OK'
            return 'ERROR'
            #print(now, 'Network is OK!!!')
        else:
            print(now, 'Network is OK!!!')
            #print(now, "Network is unreachable!!!")
            #return 'ERROR'
            return 'OK'
            #print(now, "Network is unreachable!!!")
    except Exception as e:
        print(now, e)


def send_logfile(logname):
    cmd = 'scp /home/daniel/log/'
    dst = 'root@172.29.91.109:/home/mdns'
    shell = cmd+logname+' '+dst
    try:
        net_con = netcheck()
        if net_con == 'OK':
            os.system(shell)
    except Exception as e:
        print(e)


def syslog_process(log_path,exam_minute):

    step = 1000
    # open log file to write IP
    try:
        dest_log = logfilename()
        fd_destlog = open(os.path.join(destlog_path, dest_log), 'w')
    except Exception as e:
        print('dest log file open failed!\n', e)
#        fd_destlog.close()
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
                    #print('Writing IP to log...\n')
                    fd_destlog.write(ip+'\n')
            else:
                continue
        
        fd_destlog.close()
        fd_syslog.close()
    except Exception as e:
        print('error!',e)
        #fd_syslog.close()
    
    send_logfile(dest_log)

if __name__ == '__main__':
    while True:
        delta_min = delta_minute()
        syslog_process(log_path, delta_min)
        time.sleep(60)