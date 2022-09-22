import time
from requests import get

def update_duck(ip_address):
    duck_url = "http://www.duckdns.org/update?domains=gregirving.duckdns.org&token=&ip=%s"
    update = get(duck_url % ip_address)
    
ip_new = get('https://api.ipify.org').text

update_duck(ip_new)

with open("log.txt", "w+") as log:
    log.write("Script last run: ")
    log.write(time.strftime("%H:%M:%S"))
    log.write("  ")
    log.write(time.strftime("%m/%d/%y"))
