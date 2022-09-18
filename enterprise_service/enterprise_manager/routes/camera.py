from importlib.metadata import entry_points
from time import time
from fastapi import APIRouter, HTTPException, status, Depends, Response, Security, Query
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from sqlmodel import select
from sqlalchemy.orm import load_only

from models import Camera, Site, CameraBase
from schemas import CameraUpdate
from core.database import get_session, db

from dependencies import CommonQueryParams
from core.database import redis_db
import json
import platform    # For getting the operating system name
import subprocess  # For executing a shell command
from onvif import ONVIFCamera
from camera_discovery import runWSDiscovery
camera_router = APIRouter( tags=["Camera"] )
CAMERA_DISCOVERY_LIST = []

def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """
    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'
    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]
    return subprocess.call(command) == 0

def profiling_camera(ip):
    ping_status = ping(ip)
    if not ping_status:
        return "unreachable"
    mycam = ONVIFCamera(ip, 80, 'admin', '123456a@', '/home/vietph/install/python-onvif-zeep/wsdl')
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

""" Add new cameras. """
@camera_router.post("/")
async def add_new_cameras(new_cameras: List[Camera],
                            session = Depends(get_session)) -> dict:
    for new_camera in new_cameras:
        cameras = db.get_all(session, select(Camera).where(Camera.ip == new_camera.ip))
        if cameras:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ip Supplied Is Existed"
            )

    new_cameras = [dict(camera) for camera in new_cameras]
    # Insert a bulk of data using Core
    try:
        session.execute(
            Camera.__table__.insert(),
            new_cameras
        )
        session.commit()
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail = e._message()
            )
    return {
            "Response": "New Privilege Successfully Registered!"
        }
    
""" Get site info by site name or side id. Apply for root user. """
@camera_router.get("/")
async def get_camera_by_fields(enterprise_id: int = Query(default=None),
                                site_id: int = Query(default=None),
                                id: int = Query(default=None), name: str = Query(default=None),
                                ip: str = Query(default=None), description: str = Query(default=None),
                                common_params: CommonQueryParams = Depends(),
                                session = Depends(get_session)):
    statement = select(Camera)
    if enterprise_id != None:
        sites = db.get_all(session, select(Site).options(load_only("id")).where(Site.enterprise_id == enterprise_id))
        sites_id = []
        for site in sites:
            sites_id.append(site[0].id)
        statement = statement.where(Camera.site_id.in_(sites_id))
    if site_id != None:
        statement = statement.where(Camera.site_id == site_id)
    if id != None:
        statement = statement.where(Camera.id == id)
    if name != None:
        statement = statement.where(Camera.name == name)
    if ip != None:
        statement = statement.where(Camera.ip == ip)
    if description != None:
        statement = statement.filter(Camera.description.contains(description))
    if common_params.search != None:
        statement = statement.filter(Camera.name.contains(common_params.search))
    if common_params.sort != None:
        if common_params.sort[0] == "-":
            statement = statement.order_by(Camera.name.desc())
        elif common_params.sort[0] == "+":
            statement = statement.order_by(Camera.name.asc())
    if common_params.limit != None and common_params.limit > 0:
        statement = statement.limit(common_params.limit)

    cameras = db.get_all(session, statement)
    if not cameras:
        return {"Response" : "Not Found!"}
    return [camera[0] for camera in cameras]

""" Get an camera onvif profile by ip address. """
@camera_router.get("/profiles")
async def get_camera_profile(ip: str = Query(),
                        session = Depends(get_session)):
    profile = profiling_camera(ip)
    return profile

""" Local Network Camera Discovery. """
@camera_router.get("/discovery/local")
async def discovery_camera_local_network(session = Depends(get_session)):
    ip_addrs = runWSDiscovery("239.255.255.250")
    ips_exist = []
    for ip in ip_addrs:
        cameras = db.get_all(session, select(Camera).where(Camera.ip == ip))
        if cameras:
            ips_exist.append(ip)
            
    for ip_exist in ips_exist:
        ip_addrs.remove(ip_exist)
    return ip_addrs

""" Outside Network Camera Discovery by ip address. """
@camera_router.get("/discovery/reliable")
async def discovery_camera_external_network_reliable(ip:str = Query(), session = Depends(get_session)):
    ip_addr = runWSDiscovery(ip)
    cameras = db.get_all(session, select(Camera).where(Camera.ip == ip))
    if (len(ip_addr) == 0) and cameras:
        res = ip + " Is Existed In Database, But Can Not Discovery"
        return {"Response": res}
    elif (len(ip_addr) == 1) and cameras:
        res = ip + " Is Exist In Database, And Can Discovery"
        return {"Response": res}
    else:
        return ip_addr
    
""" Outside Network Camera Discovery by ip address. """
@camera_router.get("/discovery/unreliable")
async def discovery_camera_external_network_unreliable(ip:str = Query(), session = Depends(get_session)):
    cameras = db.get_all(session, select(Camera).where(Camera.ip == ip))
    if cameras:
        res = ip + " Is Exist In Database, Does Not Discovery"
        return {"Response": res}
    ip_addr = runWSDiscovery(ip)
    return ip_addr

""" Update a camera info. """ 
@camera_router.put("/", response_model=Camera)
async def update_camera_info(body: CameraUpdate, 
                            id: int = Query(), 
                            session = Depends(get_session)):
    camera = db.get_by_id(session, select(Camera).where(Camera.id == id))
    if camera:
        camera_data = body.dict(exclude_unset=True)
        for key, value in camera_data.items():
            setattr(camera, key, value)
        camera = db.add(session, camera)  
        return camera
        
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail="Camera Supplied Id Does Not Exist"
    )
    
""" Delete a camera. Apply for root user. """
@camera_router.delete("/")
async def delete_a_camera(id: int = Query(), session = Depends(get_session)):
    camera = db.get_by_id(session, select(Camera).where(Camera.id == id))
    if camera:
        db.delete(session, camera)
        return {
            "Response": "Camera Deleted Successfully"
        }      
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Camera Supplied Id Does Not Exist"
    )