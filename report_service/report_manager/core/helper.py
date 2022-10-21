import inspect
from datetime import date, datetime
import time
from typing import Optional
def func_info():
  callerframerecord = inspect.stack()[1]    # 0 represents this line
                                            # 1 represents line at caller
  frame = callerframerecord[0]
  info = inspect.getframeinfo(frame)
  file_name = 'File "' + info.filename + '"'
  func_name = 'in ' + info.function
  line = 'line ' + str(info.lineno)
  return file_name, func_name, line

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def date_to_str(date_obj):
    if(date_obj == None or (isinstance(date_obj, date) == False)):
      return None
    try:
      return datetime.strftime(date_obj, '%Y-%m-%d')
    except ValueError as err:
      f_info = func_info()
      print('ValueError: ', f_info[0], f_info[1], f_info[2], err)

def datetime_to_str(date_obj):
    if(date_obj == None or (isinstance(date_obj, datetime) == False)):
      return None
    try:
      return datetime.strftime(date_obj, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError as err:
      f_info = func_info()
      print('ValueError: ', f_info[0], f_info[1], f_info[2], err)

def str_to_date(str_obj):
    """datetime serializer for json code"""
    try:
      return datetime.strptime(str_obj, '%Y-%m-%d')
    except ValueError as err:
      f_info = func_info()
      print('ValueError: ', f_info[0], f_info[1], f_info[2], err)

def str_to_datetime_hour(str_obj):
    """datetime serializer for json code"""
    try:
      return datetime.strptime(str_obj, '%Y-%m-%d %H')
    except ValueError as err:
      f_info = func_info()
      print('ValueError: ', f_info[0], f_info[1], f_info[2], err)
      
def str_to_datetime_minute(str_obj):
    """datetime serializer for json code"""
    try:
      return datetime.strptime(str_obj, '%Y-%m-%d %H:%M')
    except ValueError as err:
      f_info = func_info()
      print('ValueError: ', f_info[0], f_info[1], f_info[2], err)
      
def str_to_datetime_second(str_obj):
    """datetime serializer for json code"""
    try:
      return datetime.strptime(str_obj, '%Y-%m-%d %H:%M:%S')
    except ValueError as err:
      f_info = func_info()
      print('ValueError: ', f_info[0], f_info[1], f_info[2], err)
      
def str_to_datetime_milli(str_obj):
    """datetime serializer for json code"""
    try:
      return datetime.strptime(str_obj, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError as err:
      f_info = func_info()
      print('ValueError: ', f_info[0], f_info[1], f_info[2], err)
      
def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset
  
def strtime_to_utc(date_time = Optional[str]):
    if date_time == None:
        date_time = datetime.utcfromtimestamp(datetime.now().timestamp())
    else:
        split_datetime = date_time.split(" ")
        if len(split_datetime) == 1:
            print("date = ", split_datetime)
            date_time = str_to_date(date_time)
            date_time = datetime.utcfromtimestamp(date_time.timestamp())
            
        elif len(split_datetime) == 2:
            split_time = split_datetime[1].split(":")
            if len(split_time) == 1:
                print("date hour = ", split_datetime)
                date_time = str_to_datetime_hour(date_time)
                date_time = datetime.utcfromtimestamp(date_time.timestamp())
            elif len(split_time) == 2:
                print("date minute = ", split_datetime)
                date_time = str_to_datetime_minute(date_time)
                date_time = datetime.utcfromtimestamp(date_time.timestamp())
            elif len(split_time) == 3:
                if "." not in split_time[2]:
                    print("date second = ", split_datetime)
                    date_time = str_to_datetime_second(date_time)
                    date_time = datetime.utcfromtimestamp(date_time.timestamp())
                else:
                    print("date milli = ", split_datetime)
                    date_time = str_to_datetime_milli(date_time)
                    date_time = datetime.utcfromtimestamp(date_time.timestamp())
    return date_time
  
def datetime_from_utc_to_local(utc_datetime):
  now_timestamp = time.time()
  offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
  return utc_datetime + offset