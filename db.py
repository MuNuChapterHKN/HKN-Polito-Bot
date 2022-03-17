import psycopg2
from common import DATABASE_URL

def _get_db_conn():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn


def get_users_lang() -> dict[str, str]:
    users_dict: dict[str, str] = dict()
    try:
        # connect to db
        conn = _get_db_conn()
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users;")
        record = cursor.fetchone()

        # for each row, add entry in dictionary
        while record is not None:
            users_dict[str(record[0])] = str(record[1])
            record = cursor.fetchone()

    except (Exception, psycopg2.Error) as error:
        # Postgres automatically rollback the transaction
        print("Error while connecting to PostgreSQL", str(error))
    finally:
        if (conn):  # TODO: This does not solve anything
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")
            return users_dict


def get_members() -> set[int]:
    memb = set()
    try:
        # connect to db
        conn = _get_db_conn()
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members;")
        record = cursor.fetchone()

        # for each row, add entry in the list
        while record is not None:
            memb.add(record[0])
            record = cursor.fetchone()

    except (Exception, psycopg2.Error) as error:
        # Postgres automatically rollback the transaction
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if(conn):
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")
            return memb


def is_subscriber(user_id: int) -> bool:
    res = False
    try:
        conn = _get_db_conn()
        cursor = conn.cursor
        cursor.execute("SELECT * FROM subscribed WHERE id = {};".format(user_id))
        res = cursor.fetchone is not None
    except (Exception, psycopg2.Error) as error:
        # Postgres automatically rollback the transaction
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (conn):
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")
            return res
