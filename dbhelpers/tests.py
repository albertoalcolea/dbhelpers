import unittest
from mock import Mock, call

from .connections import BaseConnection
from .helpers import cm_cursor, fetchiter, fetchone_nt, fetchmany_nt, fetchall_nt, fetchiter_nt


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


class HelpersTestCase(unittest.TestCase):
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

    def test_fetchiter(self):
        cursor = Mock()

        def test_iterator(cursor, use_server_cursor=False, **kwargs):
            cursor.fetchmany = Mock(return_value=[1,2,3])
            num_it = 0
            for row in fetchiter(cursor, **kwargs):
                if num_it == 3:
                    raise StopIteration
                self.assertIn(row, [1,2,3])
                num_it += 1
                if row == 3:
                    # Stop
                    if use_server_cursor:
                        cursor.fetchall = Mock(return_value=[])
                    else:
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

        # Server cursor
        cursor.execute = Mock()
        cursor.fetchall = Mock(return_value=[1,2,3])
        test_iterator(cursor, use_server_cursor=True, size=10, server_cursor='C')
        calls = [call("FETCH %s FROM C", (10,))] * 2
        cursor.execute.assert_has_calls(calls)

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

    def test_fetchiter_nt(self):
        cursor = Mock()
        cursor.description = (('id', 3, 2, 11, 11, 0, 0), ('status', 253, 7, 80, 80, 0, 0))

        # Standard
        cursor.fetchmany = Mock(return_value=((34, 'info'), (99, 'warning')))
        num_it = 0
        for row in fetchiter_nt(cursor):
            self.assertEqual(row.__class__.__name__, 'Results')
            if num_it == 0:
                self.assertEqual(row.id, 34)
                self.assertEqual(row.status, 'info')
            if num_it == 1:
                self.assertEqual(row.id, 99)
                self.assertEqual(row.status, 'warning')
            if num_it == 2:
                raise StopIteration
            num_it += 1
            if num_it == 2:
                cursor.fetchmany = Mock(return_value=[])
        self.assertEqual(num_it, 2)

        # Batch
        cursor.fetchmany = Mock(return_value=((34, 'info'), (99, 'warning')))
        num_it = 0
        for row in fetchiter_nt(cursor, batch=True):
            self.assertEqual(row.__class__.__name__, 'list')
            self.assertEqual(row[0].__class__.__name__, 'Results')
            self.assertEqual(row[0].id, 34)
            self.assertEqual(row[0].status, 'info')
            self.assertEqual(row[1].__class__.__name__, 'Results')
            self.assertEqual(row[1].id, 99)
            self.assertEqual(row[1].status, 'warning')
            if num_it == 1:
                raise StopIteration
            num_it += 1
            if num_it == 1:
                cursor.fetchmany = Mock(return_value=[])
        self.assertEqual(num_it, 1)

        # Server cursor
        cursor.fetchall = Mock(return_value=((34, 'info'), (99, 'warning')))
        num_it = 0
        for row in fetchiter_nt(cursor, server_cursor='C'):
            self.assertEqual(row.__class__.__name__, 'Results')
            if num_it == 0:
                self.assertEqual(row.id, 34)
                self.assertEqual(row.status, 'info')
            if num_it == 1:
                self.assertEqual(row.id, 99)
                self.assertEqual(row.status, 'warning')
            if num_it == 2:
                raise StopIteration
            num_it += 1
            if num_it == 2:
                cursor.fetchall = Mock(return_value=[])
        self.assertEqual(num_it, 2)

if __name__ == '__main__':
    unittest.main()
