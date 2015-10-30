import unittest
from mock import Mock, patch

from connections import BaseConnection
from cursors import extra_cursor, cm_cursor
from helpers import fetchiter, fetchone_nt, fetchmany_nt, fetchall_nt


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

            def _connect(self_):
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

    @patch('connections.extra_cursor')
    def test_steroids(self, extra_cursor_mock):
        """
        The steroids are methods added dynamically to a new cursors of an existing
        connection instance.
        """
        cursor_mock = Mock()
        extra_cursor_mock.return_value = cursor_mock

        # Use steroids by default
        conn = self.ConnClass().connect()
        cursor = conn.cursor()
        self.assertNotEqual(cursor, self.fake_cursor)
        self.assertEqual(cursor, cursor_mock)

        # Use standard cursor by default
        concrete = self.ConnClass(steroids=False)
        conn = concrete.connect()
        cursor = conn.cursor()
        self.assertEqual(cursor, self.fake_cursor)

        # Use standard cursor by default but use the connect parameter
        conn = concrete.connect(steroids=True)
        cursor = conn.cursor()
        self.assertEqual(cursor, cursor_mock)


class CursorsTestCase(unittest.TestCase):
    @patch('cursors.helpers')
    def test_extra_cursor(self, helpers_mock):
        """
        Returns a new cursor with the `helpers` methods.
        """
        # Default call
        conn = Mock(spec=['cursor'])
        cursor_mock = Mock()
        conn.cursor = Mock(return_value=cursor_mock)

        cursor = extra_cursor(conn)
        self.assertEqual(cursor, cursor_mock)
        self.assertTrue(hasattr(cursor, 'fetchiter'))
        self.assertTrue(hasattr(cursor, 'fetchone_nt'))
        self.assertTrue(hasattr(cursor, 'fetchmany_nt'))
        self.assertTrue(hasattr(cursor, 'fetchall_nt'))

        # Call with _old_cursor
        conn = Mock(spec=['cursor', '_old_cursor'])
        cursor_mock = Mock()
        old_cursor_mock = Mock()
        conn.cursor = Mock(return_value=cursor_mock)
        conn._old_cursor = Mock(return_value=old_cursor_mock)

        cursor = extra_cursor(conn)
        self.assertEqual(cursor, old_cursor_mock)
        self.assertTrue(hasattr(cursor, 'fetchiter'))
        self.assertTrue(hasattr(cursor, 'fetchone_nt'))
        self.assertTrue(hasattr(cursor, 'fetchmany_nt'))
        self.assertTrue(hasattr(cursor, 'fetchall_nt'))

    def test_cm_cursor(self):
        """
        Creates a context manager for a cursor and it is able to commit on exit.
        """
        conn = Mock(spec=['cursor', 'commit', 'rollback'])
        cursor_mock = Mock()
        conn.cursor = Mock(return_value=cursor_mock)
        conn.commit = Mock()
        conn.rollback = Mock()

        # Commit on exit
        with cm_cursor(conn) as cursor:
            self.assertEqual(cursor, cursor_mock)
        self.assertTrue(conn.commit.called)
        self.assertFalse(conn.rollback.called)
        conn.commit.reset_mock()

        # Disable auto commit
        with cm_cursor(conn, commit=False) as cursor:
            self.assertEqual(cursor, cursor_mock)
        self.assertFalse(conn.commit.called)
        self.assertFalse(conn.rollback.called)

        # If exception no commit
        def test_with_exc(conn, commit=True):
            with cm_cursor(conn, commit=commit) as cursor:
                raise Exception()

        # If exception and commit=True, call rollback
        self.assertRaises(Exception, test_with_exc, conn=conn, commit=True)
        self.assertFalse(conn.commit.called)
        self.assertTrue(conn.rollback.called)
        conn.rollback.reset_mock()

        # If exception and commit=False, no call commit nor rollback
        self.assertRaises(Exception, test_with_exc, conn=conn, commit=False)
        self.assertFalse(conn.commit.called)
        self.assertFalse(conn.rollback.called)


class HelpersTestCase(unittest.TestCase):
    def test_fetchiter(self):
        cursor = Mock()

        def test_iterator(cursor, **kwargs):
            cursor.fetchmany = Mock(return_value=[1,2,3])
            num_it = 0
            for row in fetchiter(cursor, **kwargs):
                if num_it == 3:
                    raise StopIteration
                self.assertIn(row, [1,2,3])
                num_it += 1
                if row == 3:
                    # Stop
                    cursor.fetchmany = Mock(return_value=[])
            self.assertEqual(num_it, 3)

        # Standard
        test_iterator(cursor)

        # Size
        test_iterator(cursor, size=2)
        cursor.fetchmany.assert_called_with(2)

        # Batch
        cursor.fetchmany = Mock(return_value=[1,2])
        for row in fetchiter(cursor, batch=True):
            self.assertEqual(row, [1,2])
            # Stop
            cursor.fetchmany = Mock(return_value=[])

    def test_fetchone_nt(self):
        cursor = Mock()
        cursor.description = (('id', 3, 2, 11, 11, 0, 0), ('status', 253, 7, 80, 80, 0, 0))
        cursor.fetchone = Mock(return_value=(34, 'info'))
        r = fetchone_nt(cursor)
        self.assertEqual(r.__class__.__name__, 'Results')
        self.assertEqual(r.id, 34)
        self.assertEqual(r.status, 'info')

    def test_fetchmany_nt(self):
        cursor = Mock()
        cursor.description = (('id', 3, 2, 11, 11, 0, 0), ('status', 253, 7, 80, 80, 0, 0))
        cursor.fetchmany = Mock(return_value=((34, 'info'), (99, 'warning')))
        r = fetchmany_nt(cursor)
        self.assertEqual(r.__class__.__name__, 'list')
        self.assertEqual(r[0].__class__.__name__, 'Results')
        self.assertEqual(r[0].id, 34)
        self.assertEqual(r[0].status, 'info')
        self.assertEqual(r[1].__class__.__name__, 'Results')
        self.assertEqual(r[1].id, 99)
        self.assertEqual(r[1].status, 'warning')

    def test_fetchall_nt(self):
        cursor = Mock()
        cursor.description = (('id', 3, 2, 11, 11, 0, 0), ('status', 253, 7, 80, 80, 0, 0))
        cursor.fetchall = Mock(return_value=((34, 'info'), (99, 'warning')))
        r = fetchall_nt(cursor)
        self.assertEqual(r.__class__.__name__, 'list')
        self.assertEqual(r[0].__class__.__name__, 'Results')
        self.assertEqual(r[0].id, 34)
        self.assertEqual(r[0].status, 'info')
        self.assertEqual(r[1].__class__.__name__, 'Results')
        self.assertEqual(r[1].id, 99)
        self.assertEqual(r[1].status, 'warning')


if __name__ == '__main__':
    unittest.main()
