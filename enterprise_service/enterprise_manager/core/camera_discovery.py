from core.custom_daemon import WSDiscovery
from onvif import ONVIFCamera
import re
import time
import platform    # For getting the operating system name
import subprocess  # For executing a shell command

async def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """
    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'
    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]
    return subprocess.call(command) == 0

async def run_wsdiscovery(ip):
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

async def profiling_camera(ip):
    ping_status = await ping(ip)
    if not ping_status:
        return "unreachable"
    mycam = ONVIFCamera(ip, 80, 'admin', '123456a@', 'wsdl')
    media_service = mycam.create_media_service()
    profiles = media_service.GetProfiles()
    rtsp_list = []
    for profile in profiles:
        token = profile.token
        obj = media_service.create_type('GetStreamUri')
        obj.ProfileToken = token
        obj.StreamSetup = {'Stream': 'RTP-Unicast', 'Transport': {'Protocol': 'RTSP'}}
        stream_uri = media_service.GetStreamUri(obj)
        if stream_uri.Uri not in rtsp_list:
            rtsp_list.append(stream_uri.Uri)
    configurations_list = media_service.GetVideoEncoderConfigurations()
    stream_config_list = []
    for config in configurations_list:
        stream_data = []
        stream_data.append('encoding/' + config.Encoding)
        stream_data.append('width/' + str(config.Resolution.Width))
        stream_data.append('height/' + str(config.Resolution.Height))
        stream_data.append('framerate_limit/' + str(config.RateControl.FrameRateLimit))
        stream_data.append('bitrate_limit/' + str(config.RateControl.BitrateLimit))
        stream_data = "/".join(stream_data)
        stream_config_list.append(stream_data)
    return {"rtsp_uri": ",".join(rtsp_list), "stream": ",".join(stream_config_list)}
if __name__ == "__main__":
    print(run_wsdiscovery())