from django.db.backends.sqlite3.base import DatabaseWrapper as DjangoDatabaseWrapper
from django.db.backends.utils import CursorWrapper as DjangoCursorWrapper

import logging



logging.getLogger('main')

class CursorWrapper(DjangoCursorWrapper):
    def execute(self, sql, params=None):
        # logging.info(sql)
        return super().execute(sql, params)

class DatabaseWrapper(DjangoDatabaseWrapper):
   def create_cursor(self, name=None):
       cursor = super().create_cursor(name)
       return CursorWrapper(cursor, self)