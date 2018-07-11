import socket
import struct
import shodan
import logging
import time

SHODAN_API_KEY = "96XlzfArnJgvWyR0fwDtGa7NLdaAjgGo"

#def intIP2str(intip):
#    return socket.inet_ntoa(struct.pack('I', socket.htonl(intip)))

logging.basicConfig(filename='ip80.log',level=logging.INFO,format='%(asctime)s:%(levelname)s:%(message)s')

f = open('IP80.txt','w')

api = shodan.Shodan(SHODAN_API_KEY)

search_str = 'port:80 country:"CN"'
try:
    result = api.search(search_str)
    logging.info('[+] Total result is: %d' % result['total'])
    pages = result['total'] // 100
    if result['total'] % 100 > 0:
        pages += 1
    for n in range(1, pages+1):
        logging.info("[+] Processing page {} of {}".format(n, pages))
        #每处理50页，停止1分钟，防止shodan假死
        if n % 50 == 0:
            time.sleep(60)
        try:
            if n > 1:
                result = api.search(search_str, page = n)
            for res in result['matches']:
                if 'ip' in res:
                    ip = res['ip_str']
                    f.write(ip+'\n')
        except Exception as e:
            logging.error("[-] Error: %s"%e)
except shodan.APIError as e:
    logging.error("[-] API Error: %s"%e)

f.close()