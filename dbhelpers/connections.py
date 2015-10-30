from abc import ABCMeta, abstractmethod

import types

import getpass

from cursors import extra_cursor, cm_cursor


class BaseConnection(object):
    """
    Abstract base class for the concrete backends.

    Override the default class attributes and the _connect method according to your needs.
    """
    __metaclass__ = ABCMeta

    default_db = ''
    default_user = getpass.getuser()
    default_passwd = None
    default_host = 'localhost'
    default_port = None
    default_extra_kwargs = {}

    def __init__(self, db=None, user=None, passwd=None, host=None, port=None, steroids=True, **kwargs):
        """
        Connection with steroids.

        Valid args (if any is None, use the default class attribute):
          - db: database name/path
          - user: database username
          - passwd: database password
          - host: database host
          - port: database port
          - steroids: use a cursor with steroids instead of the standard cursor (default True)
          + Any kwargs used in the original connect method.
        """
        self.db = db if db else self.default_db
        self.user = user if user else self.default_user
        self.passwd = passwd if passwd else self.default_passwd
        self.host = host if host else self.default_host
        self.port = port if port else self.default_port
        self.extra_kwargs = self.default_extra_kwargs.copy()
        self.extra_kwargs.update(kwargs)
        self.steroids = steroids
        self.connection = None

    @abstractmethod
    def _connect(self):
        """
        Returns a connection object from the concrete backend.
        """
        pass

    @staticmethod
    def add_stereoids(connection):
        """
        Add support for the cursor with stereoids to an existing connection.
        """
        connection._old_cursor = connection.cursor
        connection.cursor = types.MethodType(extra_cursor, connection)
        connection.cm_cursor = types.MethodType(cm_cursor, connection)

    def connect(self, steroids=False):
        """
        Return a new connection.
        If stereoids = True, the cursors will be alsways a cursors with stereoids,
        else depends on the __init__ steroids param.
        """
        connection = self._connect()
        if steroids or self.steroids:
            self.add_stereoids(connection)
        return connection

    def __enter__(self):
        """
        You can use the connection class as a context manager:

        with ConcreteConnectionClass(db='mydb', user='user', passwd='passwd') as conn:
            cursor = conn.cursor()
        """
        self.connection = self.connect()
        return self.connection

    def __exit__(self, exc, value, tb):
        """
        You can use the connection class as a context manager:

        with ConcreteConnectionClass(db='mydb', user='user', passwd='passwd') as conn:
            cursor = conn.cursor()
        """
        if self.connection:
            self.connection.close()


class Psycopg2Connection(BaseConnection):
    """
    Psycopg2 backend.
    """
    default_port = 5432

    def _connect(self):
        import psycopg2
        return psycopg2.connect(database=self.db, user=self.user, password=self.passwd,
            host=self.host, port=self.port, **self.extra_kwargs)


class MySQLdbConnection(BaseConnection):
    """
    MySQLdb backend.
    """
    default_port = 3306

    def _connect(self):
        import MySQLdb
        return MySQLdb.connect(db=self.db, user=self.user, passwd=self.passwd,
            host=self.host, port=self.port, **self.extra_kwargs)


class Sqlite3Connection(BaseConnection):
    """
    Sqlite3 backend.
    """
    def _connect(self):
        import sqlite3
        return sqlite3.connect(database=self.db, **self.extra_kwargs)
