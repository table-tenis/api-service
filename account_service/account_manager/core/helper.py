import inspect
from datetime import date, datetime
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

def str_to_datetime(str_obj):
    """datetime serializer for json code"""
    try:
      return datetime.strptime(str_obj, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError as err:
      f_info = func_info()
      print('ValueError: ', f_info[0], f_info[1], f_info[2], err)