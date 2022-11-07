## **Report Service**
**Report API**

## **Requirements**
- uvicorn
- fastapi
- sqlalchemy
- sqlmodel
- pydantic
- argon2
- rsa
- pymysql
- aiomysql
- python-jose
- dynaconf
- strawberry-graphql
- pandas
## **Installation**
```
python3 -m pip install -r requirements.txt
```

## **Structure Of Report Service**
- *main.py:* to run service
- *models.py:* contains object-relational mapping model for database access.
- *schemas.py:* contains some data object to validate body requests, responses, graphql type.
- *dependencies.py:* contains dependencies for api endpoints.
- *routes:* contains api endpoints.
- *core:* contains database, helper functions.
- *config:* contains database config, SECRET_KEY config.
## **What The Report Service Do**
- Get Common Report: checkin ,checkout of all staff.
- Get Staff Report: get detection time with camera information of specific staff.
- Get Camera Report: get staff  recognized informations of  specific camera.
## **How To Build And Run**
- Build report_service docker image.
```
docker build -t report_service .
```
- Run report_service container.
```
docker-compose up -d
```

## **See Full API** 
[Report API Docs](http://172.21.100.253:3000/XFace/doc/wiki/Reporting)
