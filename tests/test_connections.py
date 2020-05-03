import unittest
from unittest.mock import Mock

from dbhelpers.connections import BaseConnection


class ConnectionsTestCase(unittest.TestCase):
    def setUp(self):
        self.fake_conn = None
        self.fake_cursor = None

        class ConcreteConnection(BaseConnection):
            default_db = 'concretedb'
            default_user = 'concreteuser'
            default_passwd = 'concretepasswd'
            default_host = 'concretehost'
            default_port = 9999
            default_extra_kwargs = {'chartset': 'ut8'}

            def connect(self_):
                """ Creates and returns a new Mock object each call """
                self.fake_conn = Mock()
                self.fake_cursor = Mock()
                self.fake_conn.cursor = Mock(return_value=self.fake_cursor)
                return self.fake_conn

        self.ConnClass = ConcreteConnection

    def test_override_attributes(self):
        """
        A concrete class can override the default attributes.
        """
        # Use the default attributes
        concrete = self.ConnClass()
        self.assertEqual(concrete.default_db, 'concretedb')
        self.assertEqual(concrete.default_user, 'concreteuser')
        self.assertEqual(concrete.default_passwd, 'concretepasswd')
        self.assertEqual(concrete.default_host, 'concretehost')
        self.assertEqual(concrete.default_port, 9999)
        self.assertEqual(concrete.default_extra_kwargs, {'chartset': 'ut8'})
        self.assertEqual(concrete.db, 'concretedb')
        self.assertEqual(concrete.user, 'concreteuser')
        self.assertEqual(concrete.passwd, 'concretepasswd')
        self.assertEqual(concrete.host, 'concretehost')
        self.assertEqual(concrete.port, 9999)
        self.assertEqual(concrete.extra_kwargs, {'chartset': 'ut8'})

        # Use mix
        concrete = self.ConnClass(db='otherdb', as_dict=True)
        self.assertEqual(concrete.default_db, 'concretedb')
        self.assertEqual(concrete.default_user, 'concreteuser')
        self.assertEqual(concrete.default_passwd, 'concretepasswd')
        self.assertEqual(concrete.default_host, 'concretehost')
        self.assertEqual(concrete.default_port, 9999)
        self.assertEqual(concrete.default_extra_kwargs, {'chartset': 'ut8'})
        self.assertEqual(concrete.db, 'otherdb')
        self.assertEqual(concrete.user, 'concreteuser')
        self.assertEqual(concrete.passwd, 'concretepasswd')
        self.assertEqual(concrete.host, 'concretehost')
        self.assertEqual(concrete.port, 9999)
        self.assertEqual(concrete.extra_kwargs, {'chartset': 'ut8', 'as_dict': True})

        # The default attributes have not been overwritten
        concrete = self.ConnClass()
        self.assertEqual(concrete.default_db, 'concretedb')
        self.assertEqual(concrete.default_user, 'concreteuser')
        self.assertEqual(concrete.default_passwd, 'concretepasswd')
        self.assertEqual(concrete.default_host, 'concretehost')
        self.assertEqual(concrete.default_port, 9999)
        self.assertEqual(concrete.default_extra_kwargs, {'chartset': 'ut8'})

    def test_connect(self):
        """
        The connect method must returns a new connection.
        """
        concrete = self.ConnClass()
        self.assertEqual(concrete.connect(), self.fake_conn)

    def test_context_manager(self):
        """
        The connection class used as a context manager must returns a new connection.
        """
        with self.ConnClass() as conn:
            self.assertEqual(conn, self.fake_conn)
