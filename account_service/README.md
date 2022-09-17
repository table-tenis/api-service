## **Account Manager Service**
**Account Manager API**

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
## **Installation**
```
python3 -m pip install -r requirements.txt
```
## **Structure Of Account Manager Service**
- *main.py:* to run service
- *models.py:* contains object-relational mapping model for database access.
- *schemas.py:* contains some data object to validate body requests, responses.
- *dependencies.py:* contains dependencies for api endpoints.
- *routes:* contains api endpoints.
- *core:* contains database and helper functions.
- *config:* contains database config, SECRET_KEY config. 
## **What The Account Manager Service Do**
### **Account API**
- Add a new account.
- Login/Logout account.
- Get account informations.
- Update an account information.
- Delete an account.
- Authenticate account using token by jwt.
- Embedded user authorization into token.
### **Access Control List API**
- Add a new acl.
- Get acl informations.
- Update an acl information.
- Delete an acl.
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
- http://172.21.100.174:9082/docs
### **Account API EndPoints**
- ```/api/xface/v1/accounts``` : POST an account, GET accounts, PUT an account, DELETE an account. Require authenticate.
  - GET method supports query parameters:
    - username: to get an account by username.
    - sort, search to sort and match accounts by username.
    - limit: to get limit number of accounts in response.
  - PUT method requires *username* query param to update an specific account.
  - DELETE method requires *username* query param to delete an specific account. Require root account.
- ```/api/xface/v1/accounts/changepassword``` : PUT to update password of an account. PUT method requires *username* query param to update password of an specific account. Require authenticate.
- ```/api/xface/v1/accounts/login``` : POST to login to system. Require *x-www-form-urlencoded* body format. Reponse token to client.
- ```/api/xface/v1/accounts/logout``` : GET to logout system. Require authenticate.
### **Access Control List API EndPoints**
- ```/api/xface/v1/acls``` : POST an acl, GET acls, PUT an acl, DELETE an acl. Require authenticate.
  - GET method supports query parameters:
    - username: to get acls by a specific account username.
    - sort, search to sort and match acls by username.
    - limit: to get limit number of acls in response.
  - PUT method requires *id* query param to update an specific acl.
  - DELETE method requires *id* query param to delete an specific acl. Require root account.


