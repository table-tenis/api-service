## **Enterprise Manager Service**
**Enterprise Manager API**

## **Requirements**
- hypercorn
- fastapi
- sqlalchemy
- sqlmodel
- pydantic
- redis
- argon2
- rsa
- mariadb
- python-jose
- netifaces
- dynaconf
- valkka
- python-onvif
## **Installation**
```
python3 -m pip install -r requirements.txt
```
### **Install Valkka For Discovery Web Service (Camera)**
```
sudo apt-add-repository ppa:sampsa-riikonen/valkka
sudo apt-get update
sudo apt-get install valkka
python -m pip install zeep
```
- **Dependencies:**
```
sudo apt-get install git build-essential libc6-dev yasm cmake pkg-config swig libglew-dev mesa-common-dev python3-dev python3-numpy libasound2-dev libssl-dev coreutils valgrind pkg-config
```
- **resource** : [github](https://github.com/elsampsa/valkka-core), [docs](https://valkka.readthedocs.io/en/latest/onvif.html).
### **Install Python-Onvif For Get Web Service Profile (Camera)**
```
python -m pip install --upgrade onvif_zeep
```
- **resource** : [github](https://github.com/FalkTannhaeuser/python-onvif-zeep).
## **Structure Of Enterprise Manager Service**
- *main.py:* to run service
- *models.py:* contains object-relational mapping model for database access.
- *schemas.py:* contains some data object to validate body requests, responses.
- *dependencies.py:* contains dependencies for api endpoints.
- *routes:* contains api endpoints.
- *core:* contains database and helper functions.
- *config:* contains database config, SECRET_KEY config.
- *camera_discovery:* contain functions to discovery cameras.
- *custom_daemon: * contains custom classes for web service discovery.
## **What The Enterprise Manager Service Do**
### **Enterprise API**
- Add new enterprise.
- Get all enterprise.
- Get enterprises by id or enterprise_code.
- Update enterprise information.
- Delete an enterprise.
### **Site API**
- Add new site.
- Get all site.
- Get all site belong to an enterprise.
- Get sites by id or site name.
- Update site information.
- Delete a site.
### **Camera API**
- Add new camera.
- Get all camera.
- Get all camera belong to an enterprise.
- Get all camera belong to an site.
- Get cameras by id, name, ip or description .
- Update camera information.
- Delete a camera.
## **How To Run**
- Build account_service docker image.
```
docker build -t account_service .
```
- Run account_service container.
```
docker-compose up -d
```
## **API Endpoint Paths**
### **Link To Test API Endpoint**
- http://172.21.100.174:9083/docs
### **Enterprise API Endpoints Paths**
- ```/api/xface/v1/enterprises``` : POST an enterprise, GET enterprises, PUT an enterprise, DELETE an enterprise. 
  - GET method supports query parameters:
    - id: to get enterprise by id.
    - enterprise_code: to get enterprise by enterprise_code.
    - sort, search to sort and match enterprise by enterprise_code.
    - limit: to get limit number of enterprise in response.
  - PUT method requires *id* query parameter to update an enterprise:
  - DELETE method requires *id* query parameter to delete an enterprise:
### **Site API Endpoints Paths**
- ```/api/xface/v1/sites``` : POST a site, GET sites, PUT a site, DELETE a site. 
  - GET method supports query parameters:
    - enterprise_id: to get sites belong to an enterprise id.
    - id: to get site by id.
    - name: to get site by name.
    - sort, search to sort and match site by name.
    - limit: to get limit number of site in response.
  - PUT method requires *id* query parameter to update a site:
  - DELETE method requires *id* query parameter to delete a site:
### **Camera API Endpoints Paths**
- ```/api/xface/v1/cameras``` : POST a list of cameras, GET cameras, PUT a camera, DELETE a camera. 
  - GET method supports query parameters:
    - enterprise_id: to get cameras belong to an enterprise id.
    - site_id: to get cameras belong to a site id.
    - id: to get camera by id.
    - name: to get camera by name.
    - ip: to get camera by ip.
    - description: to get camera by description.
    - sort, search to sort and match site by name.
    - limit: to get limit number of site in response.
- ```/api/xface/v1/cameras/profiles``` : GET profile of a camera. GET method requires ip address of camera as a query parameter:
  - ip : to get profiles of a ip address.
- ```/api/xface/v1/cameras/discovery/local``` : GET METHOD to get discovery informations of all camera in the local network.
- ```/api/xface/v1/cameras/discovery/reliable``` : Discovery a camera regardless it has existed in database. GET METHOD requires ip address of camera to discovery as a query parameter:
  - ip : to discovery of a camera ip address.
- ```/api/xface/v1/cameras/discovery/unreliable``` : Discovery a camera if it has not existed in database. GET METHOD requires ip address of camera to discovery as a query parameter:
  - ip : to discovery of a camera ip address.


