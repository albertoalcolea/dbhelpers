from collections import namedtuple


def fetchiter(cursor, size=1000, batch=False):
    """
    Use a generator as an iterator for fetching large db record sets.

    Example:
      for row in fetchiter(cursor):
        ...
    or if you use a dbhelpers cursor with stereoids:
      for row in cursor.fetchiter():
        ...
    """
    while True:
        results = cursor.fetchmany(size)
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


def fetchiter_nt(cursor, size=1000, batch=False):
    """
    Use a generator as an iterator for fetching large db record sets and return the results as
    a list of namedtuple instances.

    Example:
      for row in fetchiter_nt(cursor):
        ...
    """
    names = ' '.join(d[0] for d in cursor.description)
    klass = namedtuple('Results', names)
    for result in fetchiter(cursor, size, batch):
        if batch:
            yield map(klass._make, result)
        else:
            yield klass(*result)
