from lib2to3.pgen2.token import BACKQUOTE
from traceback import print_tb
from h11 import Data
import pymysql.cursors
from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON
import types
from pydantic import BaseModel
# Connect to the database
# connection = pymysql.connect(host='172.21.100.174',
#                              user='root',
#                              password='root',
#                              database='xface_system',
#                              cursorclass=pymysql.cursors.DictCursor)

# with connection:
#     with connection.cursor() as cursor:

def generate_class(name, dict_attr = {}):
    
    def __init__(self, method=None):
        self.method = ""
        if method != None:
            if 'select' in method:
                self.method = 'select'
            elif 'insert' in method:
                self.method = 'insert'
            elif 'delete' in method:
                self.method = 'delete'
            elif 'update' in method:
                self.method = 'update'
    
    def optional(self, *args):
        self.optional_attr = args
        return self
    
    def where(self, clause, *args):
        self.where_clause = clause % args
        return self
    
    dict_attr[optional.__name__] = optional
    dict_attr[where.__name__] = where
    dict_attr['__init__'] = __init__
    return type(name, (), dict_attr)

class NoneClass:
    def __init__(self) -> None:
        pass
    
class Base:
    __classname__ = type(NoneClass())
    def __init__(self, *args) -> None:
        self.__class__ = self.__classname__ 
        self.__init__(args)
                
def select(entity):
    return entity('select')
    
def insert(entity):
    return entity('insert')
    
def delete(entity):
    return entity('delete')

def update(entity):
    return entity('update')

class DataBase:
    class StoreORM:
        def __init__(self, data:list) -> None:
            self.data = data
            
        def all(self):
            return self.data
        
        def one(self):
            if len(self.data) > 0:
                return self.data[0]
            return []
        
    def __init__(self) -> None:
        pass
    
    def connect(self, config: dict):
        self.connection = pymysql.connect(**config)
        return self.connection
    
    def load_schema(self):
        with self.connection.cursor() as cursor:
            # Read a single record
            # sql = "SELECT `id`, `password` FROM `users` WHERE `email`=%s"
            # cursor.execute(sql, ('webmaster@python.org',))
            for subclass in Base.__subclasses__(): 
                try:
                    cursor.execute('describe ' + subclass.__tablename__)
                except Exception as e:
                    print(e)
                    break
                table_schema = cursor.fetchall()
                dict_table = {'pri_key':None}
                fields = []
                for column in table_schema:
                    # print(column)
                    data_type = column['Type']
                    if 'text' in data_type or 'varchar' in data_type or 'date' in data_type:
                        dict_table[column['Field']] = Optional[str]
                    elif 'int' in data_type:
                        dict_table[column['Field']] = Optional[int]
                    elif 'float' in data_type:
                        dict_table[column['Field']] = Optional[float]
                    else:
                        dict_table[column['Field']] = Optional[str]
                    fields.append(column['Field'])
                    if column['Key'] == 'PRI':
                        dict_table['pri_key'] = column['Field']
                dict_table['fields'] = fields
                dict_table['action'] = 'select'
                subclass.__classname__ = generate_class(subclass.__tablename__, dict_table)
                # print(subclass.__classname__.__dict__)
    def _query(self, statement):
        query = ""
        tablename = statement.__class__.__name__
        if hasattr(statement, 'optional_attr'):
            print('optional_attr = ', statement.optional_attr)
            first_insert = False
            for field in statement.optional_attr:
                if not first_insert:
                    query += "select " + tablename + "." + field
                    first_insert = True
                else:
                    query += ", " + tablename + "." + field
        else:
            query += "select * "
        query += " from " + tablename
        if hasattr(statement, 'where_clause'):
            query += " where " + statement.where_clause
        print('query = ', query)
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query)
                data = cursor.fetchall()
                return data
                result = []
                for dat in data:
                    orm = statement.__class__()
                    for key, value in dat.items():
                        setattr(orm, key, value)
                    result.append(orm)
                # return result
                return self.StoreORM(result)
            except Exception as e:
                print(e)
                
    def _insert(self, statement, args):
        query = ""
        tablename = statement.__class__.__name__
        if hasattr(statement, 'optional_attr'):
            print('optional_attr = ', statement.optional_attr)
            query += "insert into " + tablename + " ({})".format(', '.join(statement.optional_attr))
            query += " values ({})".format(', '.join(['%s' for i in range(len(statement.optional_attr))]))
        else:
            fields = []
            for field in statement.fields:
                if field != statement.pri_key:
                    fields.append(field)
            query += "insert into " + tablename + " ({})".format(', '.join(fields))
            query += " values ({})".format(', '.join(['%s' for i in range(len(fields))]))
        print(query)
        with self.connection.cursor() as cursor:
            try:
                print(args)
                cursor.executemany(query, args)
                self.connection.commit()
            except Exception as e:
                print(e)

    def _delete(self, statement):
        query = ""
        tablename = statement.__class__.__name__
        if not hasattr(statement, 'where_clause'):
            return False
        query += "delete from " + tablename + " where " + statement.where_clause
        print(query)
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query)
                self.connection.commit()
            except Exception as e:
                print(e)
    
    def _update(self, statement, args):
        query = ""
        tablename = statement.__class__.__name__
        if not hasattr(statement, 'where_clause'):
            return False
        query += "update " + tablename + " set "
        if hasattr(statement, 'optional_attr'):
            print('optional_attr = ', statement.optional_attr, args)
            for i in range(len(statement.optional_attr)):
                query += statement.optional_attr[i] + " = " + "'{}'".format(args[i])
        query += " where " + statement.where_clause
        print(query)
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query)
                self.connection.commit()
            except Exception as e:
                print(e)
    
    def execute(self, statement, args=None):
        print(args)
        if statement.method == 'select':
            return self._query(statement)
        
        elif statement.method == 'insert':
            return self._insert(statement, args)
                    
        elif statement.method == 'delete':
            return self._delete(statement)
                    
        elif statement.method == 'update':
            return self._update(statement, args)
                    
    def commit(self):
        try:
            self.connection.commit()
        except Exception as e:
            print(e)

if __name__ == '__main__':
    class Staff(Base):
        __tablename__ = 'staff'
  
    class Site(Base):
        __tablename__ = 'site'
        
    class Camera(Base):
        __tablename__ = 'camera'
        
    class StaffTest(Base):
        __tablename__ = 'staff_test'
    
    class ACL(Base):
        __tablename__ = 'acl'
        
    config = {'host':'127.0.0.1', 'user':'root', 'password':'root', 
          'database':'xface_system', 'cursorclass':pymysql.cursors.DictCursor}
    db = DataBase()
    db.connect(config)
    db.load_schema()
    
    statement = select(StaffTest)
    statement2 = insert(Site).where('email_code = %s', 'tainp')
    # print(type(statement))
    # print(type(statement2))
    # print(statement.method, statement2.method)
    
    # db.execute(statement)
    # db.execute(statement2)
    insert_statement = insert(ACL)
    delete_statement = delete(ACL).where("username = '%s'", 'root')
    update_statement = update(StaffTest).optional('email_code').where("staff_code = '277457'")
    list_data = [['277457', 'tainp3', 'tai nguyen', '1998-10-02'], ['288567', 'minhbq3', 'minh bui', '1996-11-11']]
    # db.execute(insert_statement, [['root', 'site', '1', 'admin']])
    # db.execute(delete_statement)
    data = db.execute(statement)
    print(data)
    # for dat in data:
    #     print(type(dat.id), dat.staff_code, dat.email_code, dat.fullname, dat.date_of_birth, dat.note)
        