from os import link

import psycopg2
from utils.env import DATABASE_URL


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
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (conn):
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")
            return memb


def is_subscriber(user_id: int) -> bool:
    res = False
    try:
        conn = _get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subscribed WHERE id = {};".format(user_id))
        res = cursor.fetchone() is not None
    except (Exception, psycopg2.Error) as error:
        # Postgres automatically rollback the transaction
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (conn):
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")
            return res


def add_subscriber(user_id: int) -> None:
    try:
        conn = _get_db_conn()
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subscribed VALUES ({});".format(user_id))
    except (Exception, psycopg2.Error) as error:
        # Postgres automatically rollback the transaction
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (conn):
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")


def remove_subscriber(user_id: int) -> None:
    try:
        conn = _get_db_conn()
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subscribed WHERE id = {};".format(user_id))
    except (Exception, psycopg2.Error) as error:
        # Postgres automatically rollback the transaction
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (conn):
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")


def get_subscribers() -> list[int]:
    id_list = []
    try:
        # connect to db
        conn = _get_db_conn()
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM subscribed;")
        rows = cursor.fetchall()

        # add ids to the list
        for row in rows:
            id_list.append(row[0])

    except (Exception, psycopg2.Error) as error:
        # Postgres automatically rollback the transaction
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (conn):
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")
        return id_list


def update_user_language(user_id, language):
    try:
        # connect to db
        conn = _get_db_conn()
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT lang FROM users WHERE id = '{}';".format(user_id))
        record = cursor.fetchone()
        updated = False

        # user exists, update its language
        while record:
            if language not in record:
                cursor.execute("UPDATE users SET lang = '{}' WHERE id = '{}';".format(language, user_id))
            updated = True
            break

        # user not exists, insert it with selected language
        if not updated:
            cursor.execute("INSERT INTO users(id, lang) VALUES('{}', '{}')".format(user_id, language))
    except (Exception, psycopg2.Error) as error:
        # Postgres automatically rollback the transaction
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (conn):
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")