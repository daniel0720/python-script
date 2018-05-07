import os
import time
import datetime

log_path = '/home/daniel/Desktop/cache.0170'

timedelta = 20
step = 100
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

def access_process(log_path,exam_minute):
    try:
        dest_log = logfilename()
        fd_destlog = open(dest_log,'w')
    except:
        print('dest log file open failed!\n')

    try:    
        fd_cache_log = open(log_path)
        line = fd_cache_log.readline()
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
            l = line.split('|')
            logtime = time_shift(l[8])
            if logtime >= exam_minute:
                print('Writing IP to log...\n')
                fd_destlog.write(l[0]+'\n')
    except Exception as e:
        print(e)
    finally:    
        fd_cache_log.close()
        fd_destlog.close()

if __name__ == '__main__':
    delta_min = delta_minute()
    access_process(log_path,delta_min)
