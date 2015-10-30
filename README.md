dbhelpers
=========

Database connections and cursors with stereoids.

This is not an ORM, is a set of useful utilities and helpers to work with raw queries using the Python Database API Specification.

*** UNDER DEVELOPMENT ***

Installation
------------

The easiest way to install dbhelpers is with pip:

    $ pip install dbhelpers


Usage
-----

### Connection classes

Use a default connection class for your db backend:

    from dbhelpers import Psycopg2Connection

    # Simple connection
    conn = Psycopg2Connection(db='mydb', user='myuser', passwd='mypass').connect()
    (...)
    conn.close()

    # Or using a context manager:
    with Psycopg2Connection(db='mydb', user='myuser', passwd='mypass') as conn:
        cursor = conn.cursor()
        ...

Or create a custom connection class with default parameters:

    from dbhelpers import MySQLdbConnection

    class customconn(MySQLdbConnection):
        default_user = 'myuser'
        default_passwd = 'mypass'
        default_host = 'localhost'
        default_port = 13306
        default_extra_kwargs = {'charset': 'utf8mb4'}

    with customconn('mydb') as conn:
        cursor = conn.cursor()
        ....

### Cursors with steroids

By default the default cursor is overrided with a cursor with steroids:
 * *New methods*: `fetchiter`, `fetchone_nt`, `fetchmany_nt`, `fetchall_nt`
 * *New context manager* for autocommit, autorollback and close the cursor

If you want to use the default cursor:

     conn = customconn('mydb', steroids=False).connect()
 
### Cursor as a context manager:

    # With autocommit
    with customconn('mydb') as conn:
        with cm_cursor(conn) as cursor:
            cursor.execute("INSERT INTO mytable (id, status) VALUES (23, 'info')")

    # Disable autocommit
    with customconn('mydb') as conn:
        with cm_cursor(conn, commit=False) as cursor:
            (...)

If `commit=True` (default) and an exception is thrown inside the cm_cursor with block, `cm_cursor` calls the `conn.rollback()` method instead of `conn.commit()`


### Extra methods

`fetchiter` can be used as a generator for large recordsets:

    with customconn('mydb') as conn:
        with cm_cursor(conn) as cursor:
            cursor.execute("SELECT * FROM bigtable")
            for row in cursor.fetchiter():
                # Do something

The `fetchiter` method does not retrieve all rows in memory, do sucessive calls in blocks to retrieve all data.

You can get the blocks or change the size of the block:

    with customconn('mydb') as conn:
        with cm_cursor(conn) as cursor:
            cursor.execute("SELECT * FROM bigtable")
            for block in cursor.fetchiter(size=50, batch=True)
                # Do something, block is a tuple with 50 rows


`fetchone_nt`, `fetchmany_nt` and `fetchall_nt` returns the rows as NamedTuples:

    with customconn('mydb') as conn:
        with cm_cursor(conn) as cursor:
            cursor.execute("SELECT id, status FROM mytable WHERE id = 23")
            row = cursor.fetchone_nt()
            # Now, row is a NamedTuple with each column mapped as an attribute:
            # >>> row.id
            # 32
            # >>> row.status
            # 'warning'


Also, can use the helpers functions (`fetchiter`, `fetchone_nt`, `fetchmany_nt`, `fetchall_nt`) with the standard connection and cursor classes:

    from dbhelpers.helpers import fetchiter

    conn = psycopg2.connect(database='mydb', user='user', passwd='pass', host='localhost')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM bigtable")
    for row in fetchiter(cursor):
        # Do something with row

    cursor.close()
    conn.close()
