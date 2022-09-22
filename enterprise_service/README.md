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
- pymysql
- aiomysql
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

## **Create User Tag Qualifier Tree From User Tag Qualifier**
- **Assumed, we have user1 with permission like that:**

| username  | tag_type | tag_qualifier | permissions |
| :------------- | :------------- | :-------------: | :-------------: |
| user1  | enterprise.site.camera  | 1.1.1 | crud |
| user1  | enterprise.site.camera  | 1.1.2 | crud |
| user1  | enterprise.site.camera  | 1.2.-1 | crud |
| user1  | enterprise.site.camera  | 1.3.-1 | crud |
| user1  | enterprise.site.camera  | 2.5.10 | crud |
| user1  | enterprise.site.camera  | 2.5.11 | crud |
| user1  | enterprise.site.camera  | 2.5.12 | crud |
| user1  | enterprise.site.camera  | 3.-1.-1 | crud |

- From tag qualifier set : [1,1,1], [1,1,2], [1,2,-1], [1,3,-1], [2,5,10], [2,5,11], [2,5,12], [3,-1,-1] we create user tag qualifier tree like that:

<img src="image/tag_tree_1.jpg">

- We need relable tree to have all unique node. We use a tuple include 4 fields **(depth, qualifier id, group id, parent qualifier id)** to distinct all node in tree. After that, we can construct a user tag qualifier tree like that:

<img src="image/tag_tree_2.jpg">

## **Verify Query Params With User Tag Qualifier Tree**
### **Clarify**
- **Assumed, we have user1 with permission like that:**

| username  | tag_type | tag_qualifier | permissions |
| :------------- | :------------- | :-------------: | :-------------: |
| user1  | enterprise  | 2 | admin |
| user1  | enterprise.site  | 1.2 | crud |
| user1  | enterprise.site  | 1.3 | cr-- |
| user1  | enterprise.site  | 1.4 | -r-- |
| user1  | enterprise.site  | 1.5 | -ru- |

- When user1 want to get site resources. We construct user tag qualifier tree like that:

<img src="image/tree_depth_2.jpg">

- **Case 1:** If query params **[enterprise_id, site_id] = [None, None] (or [-1, -1])**. We will prune user tag qualifier tree by query params to get matched tree. In this case matched tree is:



<img src="image/tree_depth_2_0.jpg">

- **Case 2:** If query params **[enterprise_id, site_id] = [1, None] (or [1, -1])**. Matched tree is:

<img src="image/tree_depth_2_1.jpg">

- **Case 3:** If query params **[enterprise_id, site_id] = [2, None] (or [2, -1])**. Matched tree is:

<img src="image/tree_depth_2_2.jpg">

- **Case 4:** If query params **[enterprise_id, site_id] = [2, 10]**. Matched tree is:

<img src="image/tree_depth_1_1.jpg">

- **Case 5:** If query params **[enterprise_id, site_id] = [1, 3]**. Matched tree is:

<img src="image/tree_depth_2_3.jpg">

- **Case 6:** If query params **[enterprise_id, site_id] = [1, 7]**. Matched tree is not found:

- **After Found Matched Tree. We convert matched to satisfied condition statement query. For each above case, we have condition statement is**

  - **Case 1:** (site.enterprise_id = 1 and (site.id = 2 or site.id = 3 or site.id = 4 or site.id = 5)) or (site.enterprise_id = 2)
  - **Case 2:** (site.enterprise_id = 1 and (site.id = 2 or site.id = 3 or site.id = 4 or site.id = 5))
  - **Case 3:** (site.enterprise_id = 2)
  - **Case 4:** (site.enterprise_id = 2 and site.id = 10)
  - **Case 5:** (site.enterprise_id = 1 and site.id = 3)

- **We find condition statement query by using recursive function from root of matched tree to smallest children in the matched tree**
- **These functions look like that:**
```
# gender_query to create condition statement query.
def gender_query(tree):
    if tree.key[1] == -1 and tree.key[0] != -1:
        return ""
    id = ""
    if tree.key[1] != -1:
        id = tree.name + str(tree.key[1])

    sub_id = ""
    for child in tree.children:
        if sub_id == "":
            if id != "":
                sub_id += "( " + gender_query(child)
            else:
                sub_id += gender_query(child)
        else:
            sub_id += " or " + gender_query(child)
        
    if sub_id != "":
        if id == "":
            id = "(" + sub_id + ")"
        else:
            if sub_id != "( ":
                sub_id += " )"
                id  = "( " + id + " and " + sub_id + " )"   
    return id

# Labeling for site matched tree.
def site_labeling_tree(tree):
    if tree.key[0] == -1:
        tree.name = 'root'
    elif tree.key[0] == 0:
        tree.name = 'site.enterprise_id = '
    elif tree.key[0] == 1:
        tree.name = 'site.id = '
    for child in tree.children:
        site_labeling_tree(child)

# Create condition statement query by site matched tree. 
def site_tree_to_query(tree_list):
    root = Tree((-1,-1,-1,-1))
    root.name = 'root'
    for tree in tree_list:
        root.add_child(tree)
    site_labeling_tree(root)
    # call gender_query
    return gender_query(root)   
```

### **Summary**
**To verify query params with user tag qualifier authorization tree, we have 3 steps:**
- **Step 1:** If user has permission with the resource. Create **user tag qualifier authorization tree**. Such as picture 1.
- **Step 2:** Pruning **user tag qualifier authorization tree** by **query params** to get **matched tree**.
- **Step 3:** If *matched tree** is not empty. Convert **matched tree** to **condition statement query** to filter resource.