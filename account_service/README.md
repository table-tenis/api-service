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
- Add new account.
- Login/Logout account.
- Get account information.
- Authenticate account using token by jwt.
- Embedded user authorization into token.
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
- ```/api/xface/v1/accounts``` : POST a account, GET all account information. Require super account. GET method supports query parameters: limit, sort, match by username.
- ```/api/xface/v1/accounts/{username}``` : this endpoint has path parameter *username*. PUT to update an account information by username, GET an account information by username, DELETE an account by username. Require authenticate.
- ```/api/xface/v1/accounts/{username}/changepassword``` : this endpoint has path parameter *username*. PUT to update password of an account. Require authenticate
- ```/api/xface/v1/accounts/login``` : POST to login to system. Require *x-www-form-urlencoded* body format. Reponse token to client.
- ```/api/xface/v1/accounts/logout``` : GET to logout system. Require authenticate.


