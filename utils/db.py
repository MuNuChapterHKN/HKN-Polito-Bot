import psycopg2

from utils.env import DATABASE_URL


class DatabaseFault(Exception):
    raw: psycopg2.Error

    def __init__(self, raw: psycopg2.Error):
        self.raw = raw


def _get_db_conn():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn


def get_users_lang() -> dict[str, str]:
    conn = None
    cursor = None
    users_dict: dict[str, str] = dict()
    try:
        conn = _get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users;")
        record = cursor.fetchone()

        # for each row, add entry in dictionary
        while record is not None:
            users_dict[str(record[0])] = str(record[1])
            record = cursor.fetchone()

    except psycopg2.Error as error:
        print("Error while connecting to PostgreSQL", str(error))
        raise DatabaseFault(error)
    finally:
        if conn:
            cursor.close()
            conn.close()
            return users_dict


def get_members() -> set[int]:
    conn = None
    cursor = None
    members = set()
    try:
        conn = _get_db_conn()
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members;")
        record = cursor.fetchone()

        # for each row, add entry in the list
        while record is not None:
            members.add(record[0])
            record = cursor.fetchone()

    except psycopg2.Error as error:
        print("Error while connecting to PostgreSQL", error)
        raise DatabaseFault(error)
    finally:
        if conn:
            cursor.close()
            conn.close()
            return members


def is_subscriber(user_id: int) -> bool:
    conn = None
    cursor = None
    res = False
    try:
        conn = _get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subscribed WHERE id = {};".format(user_id))
        res = cursor.fetchone() is not None
    except psycopg2.Error as error:
        print("Error while connecting to PostgreSQL", error)
        raise DatabaseFault(error)
    finally:
        if conn:
            cursor.close()
            conn.close()
            return res


def add_subscriber(user_id: int) -> None:
    conn = None
    cursor = None
    try:
        conn = _get_db_conn()
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subscribed VALUES ({});".format(user_id))
    except psycopg2.Error as error:
        print("Error while connecting to PostgreSQL", error)
        raise DatabaseFault(error)
    finally:
        if conn:
            cursor.close()
            conn.close()


def remove_subscriber(user_id: int) -> None:
    conn = None
    cursor = None
    try:
        conn = _get_db_conn()
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subscribed WHERE id = {};".format(user_id))
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        raise DatabaseFault(error)
    finally:
        if conn:
            cursor.close()
            conn.close()


def get_subscribers() -> list[int]:
    conn = None
    cursor = None
    id_list = []
    try:
        conn = _get_db_conn()
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM subscribed;")
        rows = cursor.fetchall()

        # add ids to the list
        for row in rows:
            id_list.append(row[0])

    except psycopg2.Error as error:
        print("Error while connecting to PostgreSQL", error)
        raise DatabaseFault(error)
    finally:
        if conn:
            cursor.close()
            conn.close()
        return id_list


def update_user_language(user_id, language):
    conn = None
    cursor = None
    try:
        conn = _get_db_conn()
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT lang FROM users WHERE id = '{}';".format(user_id))
        record = cursor.fetchone()
        updated = False

        while record:
            if language not in record:
                cursor.execute("UPDATE users SET lang = '{}' WHERE id = '{}';".format(language, user_id))
            updated = True
            break

        # user not exists, insert it with selected language
        if not updated:
            cursor.execute("INSERT INTO users(id, lang) VALUES('{}', '{}')".format(user_id, language))
    except psycopg2.Error as error:
        print("Error while connecting to PostgreSQL", error)
        raise DatabaseFault(error)
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_all_links() -> dict[str, str]:
    conn = None
    cursor = None
    links = dict()
    try:
        conn = _get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM links;")
        record = cursor.fetchone()

        while record is not None:
            links[record[0]] = record[1]
            record = cursor.fetchone()
    except psycopg2.Error as error:
        print("Error while connecting to PostgreSQL", error)
        raise DatabaseFault(error)
    finally:
        if conn:
            cursor.close()
            conn.close()

        return links
