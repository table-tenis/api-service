import pymysql.cursors
from core.helper import datetime_to_str
config = {
    'host': '172.21.100.167',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'xface_system'
}

conn = pymysql.connect(**config)


with conn.cursor() as cursor:
    start_time = "2022-10-14"
    end_time = "2022-10-16"
    statement = f"select staff.staff_code, staff.email_code, staff.fullname, staff.unit, b.min_time, b.max_time "\
                    "from staff left outer join (select staff_id, Min(detection_time) as min_time, Max(detection_time) as max_time "\
                                                "from detection "\
                                                "where (detection_time >= '{}') and (detection_time <= '{}') "\
                                                "group by staff_id) as b "\
                    "on staff.id = b.staff_id "\
                    "where staff.state != 0;".format(start_time, end_time)
    print("statement = ", statement)
    cursor.execute(statement)
    staffs = cursor.fetchall()
    list_data = []
    for staff in staffs:
        # print(staffs, type(staffs))
        list_data.append({'staff_code':staff[0], 'mail_code':staff[1], 'fullname':staff[2], 'unit':staff[3], 
                          'checkin':datetime_to_str(staff[4]), 'checkout':datetime_to_str(staff[5])})
    
    print(len(list_data))
                    