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
- tag_type: type of privilege.
- tag_qualifier: identifies a specific resource (id,...)
- permissions: specifies the permissions (create(c), read(r), update(u), delete(d), admin).

| username  | tag_type | tag_qualifier | permissions |
| :------------- | :------------- | :-------------: | :-------------: |
| vtx.admin  | enterprise  | 1 | admin |
| vtx.site1  | enterprise.site  | 1.1 | admin |
| vtx.site1.c  | enterprise.site  | 1.1 | c--- |
| vtx.site1.r  | enterprise.site  | 1.1 | -r-- |
| vtx.site1.r  | enterprise.site  | 1.1 | --u- |
| vtx.site1.d  | enterprise.site  | 1.1 | ---d |
| vtx.site1.cr  | enterprise.site  | 1.1 | cr-- |
| vtx.site1.crud  | enterprise.site  | 1.1 | crud |
| vtx.site2  | enterprise.site  | 1.2 | admin |
| vht.admin  | enterprise  | 2 | admin |
| vht.site.all_priv  | enterprise.site  | 2.-1 | admin |
| vht.site.all_crud  | enterprise.site  | 2.-1 | crud |
| enterprise.all_priv  | enterprise  | -1 | admin |
| enterprise.all_cr  | enterprise  | -1 | cr-- |

- id qualifier = -1 to alter '*' charater for converting easily string to int.

### **Authorization Encode To String Example**
- Example, we have access control list table for vtx_user like this:

| username  | tag_type | tag_qualifier | permissions |
| :------------- | :------------- | :-------------: | :-------------: |
| vtx_user  | enterprise  | 2 | admin |
| vtx_user  | enterprise.site  | 1.1 | admin |
| vtx_user  | enterprise.site  | 1.2 | c--- |
| vtx_user  | enterprise.site  | 1.3 | -r-- |
| vtx_user  | enterprise.site  | 1.4 | --u- |
| vtx_user | enterprise.site.camera  | 1.1.-1 | cru- |

- **_authorization encode_** = ```'enterprise:2:admin|enterprise.site:1.1,1.2,1.3,1.4:admin,c---,-r--,--u-|enterprise.site.camera:1.1.-1:cru-'```
  - **_authorization encode_** above comprise 3 **compound acl record**, separated by '|' character.
  - tag_type, tag_qualifiers, permissions is separated by ':' character in each **compound acl record**.
  - Each **compound acl record** have unique tag_type such that *enterprise* in first **compound acl record**, *enterprise.site* in second **compound acl record**, *enterprise.site.camera* in third **compound acl record**.
  - tag_qualifiers in each **compound acl record** is separated by ',' character. Such as, with tag_type is *enterprise.site*, vtx_user has 4 tag_qualifier is '1.1', '1.2', '1.3', '1.4'. So in *enterprise.site* **compound acl record**, tag_qualifiers = ```'1.1,1.2,1.3,1.4'```
  - Similar to tag_qualifiers, permissions in *enterprise.site* **compound acl record** = ```'admin,c---,-r--,--u-'```.
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


