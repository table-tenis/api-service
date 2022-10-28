import requests
from json import loads
from io import StringIO
import pandas as pd
# defined a URL variable that we will be
# using to send GET or POST requests to the API
url = "http://0.0.0.0:9032/graphql/"
 
body = """
{
  getReport(queryParams:{emailCode:"tainp"}){
    staffCode,
    emailCode,
    fullname,
    dateOfBirth,
    report{
      checkin,
      checkout,
      reportDate
    }
  }
}
"""

query_string = """
    query getUser($id: ID) {
        me(id: $id) {
            id
            name
        }
    }
 """
variables = {"id": 12}
response = requests.get(url=url)
print("response status code: ", response.status_code)
if response.status_code == 200:
  print(response.content)
  
  s=str(response.content,'utf-8')

  data = StringIO(s) 

  df=pd.read_csv(data)
  df.to_csv("report_tmp.csv")
  # data = loads(response.content)
  # print(data)
  # for key, value in data.items():
  #   print(key)
  # print(data['getReport'])
  # print(response.headers['X-Process-Time'])