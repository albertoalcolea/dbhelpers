import helpers

import types


def extra_cursor(connection, **kwargs):
    """
    Add dynamically the stereoids to a standard cursor
    """
    if hasattr(connection, '_old_cursor'):
        cursor = connection._old_cursor(**kwargs)
    else:
        cursor = connection.cursor(**kwargs)
    cursor.fetchiter = types.MethodType(helpers.fetchiter, cursor)
    cursor.fetchone_nt = types.MethodType(helpers.fetchone_nt, cursor)
    cursor.fetchmany_nt = types.MethodType(helpers.fetchmany_nt, cursor)
    cursor.fetchall_nt = types.MethodType(helpers.fetchall_nt, cursor)
    return cursor


class cm_cursor(object):
    """
    Aux class to use a cursor with a context manager and commit the changes when the cursor
    is closed.
    If it is called with commit=False the cursor is closed without commit anything.
    """
    def __init__(self, connection, commit=True, **kwargs):
        self.connection = connection
        self.cursor = connection.cursor(**kwargs)
        self.commit = commit

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc, value, tb):
        if self.commit:
            if exc:
                self.connection.rollback()
            else:
                self.connection.commit()
        self.cursor.close()
