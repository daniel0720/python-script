import os
import time
import datetime

cache_path = '/data/dnslog1/'
cache_log = '/home/daniel/log/cache.log'
destlog_path = '/home/daniel/log/'
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
    ms = strtime.split('.')[1]
    logtime = time.strptime(strtime.split('.')[0],'%Y%m%d%H%M%S')
    logtm = datetime.datetime(*logtime[:6]).timestamp()
    logt = str(logtm).split('.')[0]+'.'+ ms
    return float(logt)


def send_logfile(logname):
    cmd = 'scp '+destlog_path
    dst = 'root@172.29.91.109:/home/mdns'
    shell = cmd+logname+' '+dst
    try:
        os.system(shell)
    except Exception as e:
        print(e)

def getnewestfile(file_path):
    filelist = os.listdir(file_path)
    filelist.sort(key = lambda fn: os.path.getmtime(os.path.join(file_path, fn)))
    filepath = os.path.join(file_path, filelist[-1])
    return filepath

def gz2txt(log_path):
    os.system('zcat '+log_path+' > '+cache_log)

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
            log_time = line.split('|')[8]
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
            ln = line.split('|')
            logtime = time_shift(ln[8])
            #print(ln)
            if logtime >= exam_minute:
                #print('Writing IP to log...\n')
                #print(ln[-1])
                if ln[-1] == 'q\n':
                    fd_destlog.write(ln[0]+'\n')
        
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
        cachelog = getnewestfile(cache_path)
        gz2txt(cachelog)
        access_process(cache_log, delta_min)
        time.sleep(60)
