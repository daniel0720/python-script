import os
import time
from datetime import datetime, timedelta
from scapy.all import *

logpath = '/home/daniel/workspace/qwb/dns/dns-log/tcpdump-log'

nine_clock = 'May 10 09:00:00 2018'
time_fmt = '%b %d %H:%M:%S %Y'

team_net = ['10.10.1','10.10.2','10.10.3','10.10.4','10.10.5','10.10.6','10.10.7','10.10.8','10.10.9','10.10.10',\
                '10.10.11','10.10.12','10.10.13','10.10.14','10.10.15','10.10.16','10.10.17','10.10.18','10.10.19','10.10.20',\
                '10.10.21','10.10.22']
per_hour_ts = []           # 每小时的时间戳列表
per_hour_str = []
#total_attack = 0        # 总的攻击次数
per_team_attack = {}    # 每队的攻击次数，key=网络号，value=攻击次数
unknow_attack = {}
per_hour_attack = {}


# 生成每小时的时间戳列表
def per_hour_gen():    
    nine_time = datetime.strptime(nine_clock, time_fmt)
    now_time = nine_time
    per_hour_ts.append(now_time.timestamp())
    per_hour_str.append(nine_clock)
    for i in range(54):
        now_time = now_time + timedelta(hours = 1)
        per_hour_ts.append(now_time.timestamp())
        now_time_str = datetime.strftime(now_time,time_fmt)
        per_hour_str.append(now_time_str)

def init_per_hour_attack():
    for i in range(len(per_hour_str)):
        per_hour_attack[per_hour_str[i]] = 0


# 时间比较，返回时间段
def hour_attack(timestamps):
    for i in range(len(per_hour_ts)):
        if timestamps < per_hour_ts[i]:
            #return i
            if i > 0:
                ts = per_hour_ts[i-1]
                hour_str = time.strftime(time_fmt, time.localtime(ts))
                #print("hour attack: ", hour_str)
                per_hour_attack[hour_str] += 1
            break


# 处理IP地址，提取网络号
def ip_net_id(ip_addr):
    ip = ip_addr.split('.')
    return(ip[0]+'.'+ip[1]+'.'+ip[2])


# 统计每个队的攻击次数，存放在per_team_attack字典中
def team_attack(net_id):
    if net_id in team_net:
        if net_id in per_team_attack:
            per_team_attack[net_id] += 1
        else:
            print(net_id," attacked!")
            per_team_attack[net_id] = 1
    elif net_id in unknow_attack:
        unknow_attack[net_id] += 1
    else:
        print(net_id," attacked!")
        unknow_attack[net_id] = 1


def main_process():
    total_attack = 0
    ping_count = 0
    for root, dirs, files in os.walk(logpath):
        for name in files:
            print("Processing ",name,' ......')
            ping = 0
            pcapname = os.path.join(root, name)
            fpcap = rdpcap(pcapname)
            for i in range(len(fpcap)):
                packet = fpcap[i]
                # 过滤ping数据包
                if packet.haslayer(ICMP):
                    #print('ICMP packet')
                    ping_count += 1
                    ping += 1
                    continue
                # 过滤二层数据包
                if packet.haslayer(IP):
                    total_attack += 1
                    netid = ip_net_id(packet[IP].src)
                    #print(netid)
                    team_attack(netid)
                    if packet[IP].src == '10.10.199.233':
                        continue
                    hour_attack(packet.time)
            print('ping: ', ping)
    print("total ping count: ", ping_count)
    return total_attack


def write_result(total_att):
    result = open('log_result.txt', 'w+')
    result.write('per hour attack: \n')
    for key, value in per_hour_attack.items():
        result.write(key+":"+str(value))
        result.write('\n')
    
    result.write('\n')
    result.write('per team attack: \n')
    for key, value in per_team_attack.items():
        result.write(key+":"+str(value))
        result.write('\n')
    
    result.write('\n')
    result.write('unkonw attack: \n')
    for key, value in unknow_attack.items():
        result.write(key+":"+str(value))
        result.write('\n')
    
    t = 'Total attack: ' + str(total_att)
    result.write(t)
        
    result.close()

if __name__ == '__main__':
    per_hour_gen()
    init_per_hour_attack()
    total = main_process()
    write_result(total)