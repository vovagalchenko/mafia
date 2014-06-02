from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, func
from sqlalchemy.dialects import mysql
from datetime import datetime

Base = declarative_base()

class Mafia_Model_Mixin(object):
    __table_args__ = {'mysql_engine' : 'InnoDB'}

    created = Column(mysql.TIMESTAMP, nullable = False, server_default = func.current_timestamp())
    updated = Column(mysql.TIMESTAMP, nullable = False, server_default = func.current_timestamp(), onupdate = func.current_timestamp())
    # Below is a hack to make sure the mixin columns are added to the end of the actual model columns
    updated._creation_order = 9998
    created._creation_order = 9999

    def for_api(self):
        ret_value = {}
        for column_name in self.__mapper__.columns.keys():
            column_value = getattr(self, column_name)
            ret_value[column_name] = column_value
        return ret_value
