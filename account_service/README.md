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
### **Access Control List Table**
- username: username of account.
- tag_type: type of privilege (site, staff, camera, site.camera,...).
- tag_qualifier: identifies a specific resource (id,...)
- permissions: specifies the permissions (create(c), read(r), update(u), delete(d), admin).

| username  | tag_type | tag_qualifier | permissions |
| :------------- | :------------- | :-------------: | :-------------: |
| site1.admin  | site  | 1 | admin |
| site1.create  | site  | 1 | c--- |
| site1.read  | site  | 1 | -r-- |
| site2.update  | site  | 2 | --u- |
| site2.delete  | site  | 2 | ---d |
| site1.cr  | site  | 1 | cr-- |
| site1.crud  | site  | 1 | crud |
| all_site.admin  | site  | -1 | admin |
| all_site.cr  | site  | -1 | cr-- |

- id qualifier = -1 to alter '*' charater for converting easily string to int.

### **Authorization Encode To String Example**
- Example, we have access control list table for vtx_user like this:

| username  | tag_type | tag_qualifier | permissions |
| :------------- | :------------- | :-------------: | :-------------: |
| vtx_user  | site  | 1 | admin |
| vtx_user  | site  | 2 | c--- |
| vtx_user  | site  | 3 | -r-- |
| vtx_user  | site  | 4 | --u- |
| vtx_user | site.camera  | 4.-1 | -ru- |

- **_authorization encode_** = ```'site:1,2,3,4:admin,c---,-r--,--u-|site.camera:4.-1:-ru-'```
  - **_authorization encode_** above comprise 2 **compound acl record**, separated by '|' character.
  - tag_type, tag_qualifiers, permissions is separated by ':' in each **compound acl record**.
  - Each **compound acl record** have unique tag_type such that *site* in first **compound acl record**, *site.camera* in second **compound acl record**.
  - tag_qualifiers in each **compound acl record** is separated by ','. Such as, with tag_type is *site*, vtx_user has 4 tag_qualifier is '1', '2', '3', '4'. So in *site* **compound acl record**, tag_qualifiers = ```'1,2,3,4'```
  - Similar to tag_qualifiers, permissions in *site* **compound acl record** = ```'admin,c---,-r--,--u-'```.
- **_authorization encode_** will be encoded with token when user sign-in to system. After that, this data will be used to verify resources authorization when receive requests.

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


