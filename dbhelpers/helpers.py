from collections import namedtuple


class cm_cursor(object):
    """
    Aux class to use a cursor with a context manager and commit the changes when the
    cursor is closed.
    If it is called with commit=False the cursor is closed without commit anything.
    If an exception is thrown and commit=True, calls the connection.rollback method.
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
        if self.cursor:
            self.cursor.close()


def fetchiter(cursor, size=1000, batch=False, server_cursor=None):
    """
    Use a generator as an iterator for fetching large db record sets.

    Example:
      for row in fetchiter(cursor):
        ...

    Only for PostgreSQL
    -------------------
    You can use a previous server cursor declared as:
    `DECLARE {C} CURSOR FOR SELECT * FROM ...` where {C} is a string with the
    server cursor name.

    Then use the parameter server_cursor={C} where {C} is the cursor name,
    this will make each iteration runs `FETCH {size} FROM {C}` instead of the
    whole query.
    """
    while True:
        if server_cursor is None:
            # Standar cursor
            results = cursor.fetchmany(size)
        else:
            # PostgreSQL server side cursor
            cursor.execute("FETCH %s FROM {}".format(server_cursor), (size,))
            results = cursor.fetchall()
        if not results:
            break
        if batch:
            yield results
        else:
            for result in results:
                yield result


def fetchone_nt(cursor):
    """
    Return the results of a query as a namedtuple instance.
    """
    names = ' '.join(d[0] for d in cursor.description)
    klass = namedtuple('Results', names)
    db_res = cursor.fetchone()
    if db_res is None:
        return None
    else:
        results = klass(*db_res)
        return results


def fetchmany_nt(cursor, size=None):
    """
    Return the results of a query as a list of namedtuple instances.
    """
    if size is None:
        size = cursor.arraysize
    names = ' '.join(d[0] for d in cursor.description)
    klass = namedtuple('Results', names)
    db_res = cursor.fetchmany(size)
    if not db_res or db_res is None:
        return []
    else:
        results = map(klass._make, db_res)
        return results


def fetchall_nt(cursor):
    """
    Return the results of a query as a list of namedtuple instances.
    """
    names = ' '.join(d[0] for d in cursor.description)
    klass = namedtuple('Results', names)
    db_res = cursor.fetchall()
    if not db_res or db_res is None:
        return []
    else:
        results = map(klass._make, db_res)
        return results


def fetchiter_nt(cursor, size=1000, batch=False, server_cursor=None):
    """
    Use a generator as an iterator for fetching large db record sets and return the
    results as a list of namedtuple instances.

    Example:
      for row in fetchiter_nt(cursor):
        ...

    Only for PostgreSQL
    -------------------
    You can use a previous server cursor declared as:
    `DECLARE {C} CURSOR FOR SELECT * FROM ...` where {C} is a string with the
    server cursor name.

    Then use the parameter server_cursor={C} where {C} is the cursor name,
    this will make each iteration runs `FETCH {size} FROM {C}` instead of the
    whole query.
    """
    names = ' '.join(d[0] for d in cursor.description)
    klass = namedtuple('Results', names)
    for result in fetchiter(cursor, size, batch, server_cursor):
        if batch:
            yield map(klass._make, result)
        else:
            yield klass(*result)
