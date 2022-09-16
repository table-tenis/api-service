from custom_daemon import WSDiscovery
import re
import time
def runWSDiscovery(ip):
    reg = re.compile("^http:\/\/(\d*\.\d*\.\d*\.\d*).*\/onvif")
    wsd = WSDiscovery()
    ip_range = [ip]
    wsd.start()
    start_time = time.time()
    ws_devices = wsd.searchServiceInRange(ip_range)
    end_time = time.time() - start_time
    print("search services time = ", end_time, " seconds")
    ip_addresses = []
    print(ws_devices)
    for ws_device_range in ws_devices:
        for ws_device in ws_device_range:
            for http_address in ws_device.getXAddrs():
                m = reg.match(http_address)
                if m is None:
                    continue
                else:
                    ip_address = http_address[m.start(1):m.end(1)]
                    # print(ip_address)
                    ip_addresses.append(ip_address)
    wsd.stop()
    return ip_addresses

if __name__ == "__main__":
    print(runWSDiscovery())