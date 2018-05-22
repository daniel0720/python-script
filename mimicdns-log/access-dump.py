import os
import time
import datetime
import subprocess

destlog_path = '/home/daniel/log/'
dump_path = '/home/daniel/dump/'
cachelog = '/home/daniel/cachedns.txt'
timedelta = 1
step = 10
#返回timedelta分钟前的时间戳
def delta_minute():
    a = (datetime.datetime.today()-datetime.timedelta(minutes=timedelta)).timestamp()
    return a

def logfilename():
    easytime = time.strftime('%Y%m%d%H%M',time.localtime())
    file_name = 'dns_access_%s.log' %easytime
    return file_name

def time_shift(strtime):
    st = strtime.split('.')
    ms = st[1]
    hms = st[0].split(':')
    today = datetime.datetime.today()
    td = today.replace(hour=int(hms[0]),minute=int(hms[1]),second=int(hms[2]),microsecond=int(ms))
    ptime = td.timestamp()
    
    return ptime

def ip_extract(ip_port):
    ip_tuple  = ip_port.split('.')
    ip = ip_tuple[0]+'.'+ip_tuple[1]+'.'+ip_tuple[2]+'.'+ip_tuple[3]
    return ip


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
        else:
            print(now, 'Network is OK!!!')
            #print(now, "Network is unreachable!!!")
            #return 'ERROR'
            return 'OK'
    except Exception as e:
        print(now, e)


def send_logfile(logname):
    cmd = 'scp '+destlog_path
    dst = 'root@172.29.91.109:/home/mdns'
    shell = cmd+logname+' '+dst
    try:
        net_con = netcheck()
        if net_con == 'OK':
            os.system(shell)   

    except Exception as e:
        print(e)

#def getnewestfile(file_path):
#    filelist = os.listdir(file_path)
#    filelist.sort(key = lambda fn: os.path.getmtime(os.path.join(file_path, fn)))
#    filepath = os.path.join(file_path, filelist[-1])
#    return filepath


def access_process(log_path, exam_minute):
    try:
        dest_log = logfilename()
        fd_destlog = open(os.path.join(destlog_path, dest_log), 'w')
    except Exception as e:
        print('dest log file open failed!\n', e)
        

    try:    
        fd_cache_log = open(log_path)
        line = fd_cache_log.readline()
        #print(line)
        while line:
            log_time = line.split()[0]
            logtime = time_shift(log_time)
            if logtime >= exam_minute:
                fd_cache_log.seek(fd_cache_log.tell() - step)
                fd_cache_log.readline()       #将该行读完         
                break
            fd_cache_log.seek(fd_cache_log.tell() + step)
            if fd_cache_log.tell() >= os.path.getsize(log_path):
                fd_cache_log.seek(fd_cache_log.tell() - step)
                fd_cache_log.readline()
                break
            fd_cache_log.readline()
            line = fd_cache_log.readline()
        
        for line in fd_cache_log:
            ln = line.split()
            logtime = time_shift(ln[0])
            if logtime >= exam_minute:
                #print('logtime:',logtime)
                #print('exam_time:',exam_minute)
                #print('Writing IP to log...\n')
                ip = ip_extract(ln[2])
                fd_destlog.write(ip+'\n')
        
        fd_cache_log.close()
        fd_destlog.close()
    except Exception as e:
        print(e)
        #fd_cache_log.close()
        #fd_destlog.close()

    send_logfile(dest_log)


if __name__ == '__main__':
    while True:
        delta_min = delta_minute()
#        cachelog = getnewestfile(dump_path)
        access_process(cachelog, delta_min)
        time.sleep(60)
