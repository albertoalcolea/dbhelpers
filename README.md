dbhelpers
=========

[![Build Status](https://travis-ci.org/albertoalcolea/dbhelpers.svg?branch=master)](https://travis-ci.org/albertoalcolea/dbhelpers)

Database helpers and utilities

This is not an ORM, is a set of useful utilities to work with raw queries using the Python Database API Specification.


Installation
------------

The easiest way to install dbhelpers is with pip:

    $ pip install dbhelpers


Usage
-----

### Connection classes

Use a default connection class for your db backend:

```python
from dbhelpers import Psycopg2Connection

# Simple connection
conn = Psycopg2Connection(db='mydb', user='myuser', passwd='mypass').connect()
(...)
conn.close()

# Or using a context manager:
with Psycopg2Connection(db='mydb', user='myuser', passwd='mypass') as conn:
    cursor = conn.cursor()
    ...
```

Or create a custom connection class with your default parameters:

```python
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
```

### Helpers

The package include some useful utilities to work with database cursors.

#### Cursor as a context manager:

The cursor is executed inside a `with` block. When the block ends the cursor is closed. Also does a `connection.commit()` when the block ends if `commit=True` (True by default).

```python
from dbhelpers import cm_cursor

# With autocommit
with customconn('mydb') as conn:
    with cm_cursor(conn) as cursor:
        cursor.execute("INSERT INTO mytable (id, status) VALUES (23, 'info')")

# Disable autocommit
with customconn('mydb') as conn:
    with cm_cursor(conn, commit=False) as cursor:
        (...)
```

If `commit=True` (default) and an exception is thrown inside the `with` block, `cm_cursor` calls the `conn.rollback()` method instead of `conn.commit()`

In Python 2.7 and 3.x you can get the connection object and the cursor object of the context managers in a single with statment:

```python
with customconn('mydb') as conn, cm_cursor(conn) as cursor:
    # Do something ...
```

#### Fetchiter

`fetchiter` can be used as a generator for large recordsets:

```python
from dbhelpers import fetchiter

with customconn('mydb') as conn:
    with cm_cursor(conn) as cursor:
        cursor.execute("SELECT * FROM bigtable")
        for row in fetchiter(cursor):
            # Do something
```

The `fetchiter` function does not copy all rows in memory, do sucessive calls in blocks to retrieve all data. The default block size is 1000.

The `cursor.fetchall()` method can fill the process memory easily if there are a lot of register to return. `fetchiter` do calls to `cursor.fetchmany()` iteratively until there are no more data  to return. The `fetchiter` function behaves like an iterator.

You can get the whole blocks or change the size of the block:

```python
with customconn('mydb') as conn:
    with cm_cursor(conn) as cursor:
        cursor.execute("SELECT * FROM bigtable")
        for block in fetchiter(cursor, size=50, batch=True):
            # Do something, block is a tuple with 50 rows
```

#### PostgreSQL server cursor

Also, `fetchiter` allows work with PostgreSQL server cursors previously declared.

Instead of the standard `fetchiter` behavior, which do a query to a server, the server calculates the whole recordset, and `fetchiter` retrieve the results iteratively to avoid fill the process memory, a server cursor runs the pseudo-iterator on a Postgres server and calculates the partial recordset in blocks iteratively. 

```python
from dbhelpers import fetchiter

with customconn('mydb') as conn:
    with cm_cursor(conn) as cursor:
        cursor.execute("DECLARE C CURSOR FOR SELECT * FROM bigtable")
        for row in fetchiter(cursor, server_cursor='C'):
            # Do something
        cursor.execute("CLOSE C")
```

`fetchiter` can return the server cursor results as the above example (as an interator or as a block), an you can change the block size. The default block size is 1000.

#### Rows as NamedTuples

`fetchone_nt`, `fetchmany_nt`, `fetchall_nt` `fetchiter_nt` returns the rows as NamedTuples:

```python
from dbhelpers import fetchone_nt, fetchmany_nt, fetchall_nt

with customconn('mydb') as conn:
    with cm_cursor(conn) as cursor:
        cursor.execute("SELECT id, status FROM mytable WHERE id = 23")
        row = fetchone_nt(cursor)
        # Now, row is a NamedTuple with each column mapped as an attribute:
        # >>> row.id
        # 32
        # >>> row.status
        # 'warning'
```

