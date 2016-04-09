import sqlite3
from datetime import datetime, timedelta, date

# DB STATIC VARIABLES

DB_NAME = 'database/feed.db'
DB_CREATE_NAME = 'database/feed.sql'
DB_TABLES = ['ITEM',
             'CATEGORY',
             'ITEM_has_CATEGORY']

# CONNECTION

connection = None

# DB HELPER FUNCTIONS


def open_connection():
    """
        Opens the connection to the database file.
        :return The cursor of the connection.
    """
    global connection
    connection = sqlite3.connect(DB_NAME)
    return connection.cursor()


def close_connection():
    """
        Closes the connection to the database file.
    """
    global connection
    connection.commit()
    connection.close()


def create_tables():
    """
        Checks if the tables in array DB_TABLES exist.
        If they don't exist it executes the create tables script in DB_CREATE_NAME.
    """
    if not check_if_tables_exist():
        try:
            cursor = open_connection()
            f = open(DB_CREATE_NAME, 'r')
            sql = f.read()
            cursor.executescript(sql)
        finally:
            close_connection()


def drop_tables():
    """
        Checks if the tables in array DB_TABLES exist.
        If they do exist it executes the drop table command.
    """
    try:
        cursor = open_connection()
        for table_name in DB_TABLES:
            cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name=?;', (table_name,))
            if cursor.fetchone() is not None:
                cursor.execute('DROP TABLE ' + table_name)
    finally:
        close_connection()


def check_if_tables_exist():
    """
        Checks if the tables in array DB_TABLES exist.
        :return True if they all exist. False if one of them doesn't exist.
    """
    try:
        cursor = open_connection()
        exist = True
        for table_name in DB_TABLES:
            cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name=?;', (table_name,))
            if cursor.fetchone() is None:
                exist = False
        return exist
    finally:
        close_connection()


# DB FUNCTIONS


def get_all_items():
    """
        :return A list containing all the items.
    """
    try:
        cursor = open_connection()
        cursor.execute('SELECT guid,title, description, pubDate, author FROM ITEM ORDER BY pubDate DESC ;')
        response = []
        for item in cursor.fetchall():
            response.append({
                'guid': item[0],
                'title': item[1],
                'description': item[2],
                'pubDate': item[3],
                'author': item[4],
                'categories': get_categories(item[0], cursor)
            })
        return response
    finally:
        close_connection()


def get_item(item_guid):
    """
        :param item_guid The guid of the item to retrieve from the database.
        :type item_guid String
        :return The item with the specified guid.
    """
    try:
        cursor = open_connection()
        cursor.execute('SELECT guid,title, description, pubDate, author FROM ITEM WHERE guid=? ORDER BY pubDate DESC;', (item_guid,))
        result = cursor.fetchone()
        if result is not None:
            result = {
                    'guid': result[0],
                    'title': result[1],
                    'description': result[2],
                    'pubDate': result[3],
                    'author': result[4],
                    'categories': get_categories(result[0], cursor)
                }
        return result
    finally:
        close_connection()


def save_item(guid, title, description, pub_date, author, categories):
    """
        :param guid The guid of the item to save in the database.
        :type guid String
        :param title The title of the item to save in the database.
        :type title String
        :param description The description of the item to save in the database.
        :type description String
        :param pub_date The pubDate of the item to save in the database.
        :type pub_date Integer
        :param author The author of the item to save in the database.
        :type author String
        :param categories The categories of the item to save in the database.
        :type categories Array of tuple
        :return The item with the specified guid.
    """
    try:
        cursor = open_connection()
        cursor.execute('INSERT INTO ITEM (guid,title, description, pubDate, author) VALUES (?,?,?,?,?)',
                       (guid, title, description, pub_date, author,))
        for (url, text) in categories:
            exists = category_exists(url, cursor)
            if not exists:
                cursor.execute('INSERT INTO CATEGORY (url, "text") VALUES (?,?)', (url, text,))
            cursor.execute('INSERT INTO ITEM_has_CATEGORY (item_guid, category_url) VALUES (?,?)', (guid, url,))
        return cursor.lastrowid
    finally:
        close_connection()


def get_categories(item_guid, cursor):
    """
        :param item_guid The guid of the item to retrieve the categories from the database.
        :type item_guid String
        :return The categories from the item with the specified guid.
    """
    cursor.execute('SELECT c.url, c."text" FROM CATEGORY c INNER JOIN ITEM_has_CATEGORY ihc '
                   'ON (c.url = ihc.category_url) WHERE ihc.item_guid=?', (item_guid,))
    response = []
    for category in cursor.fetchall():
        response.append((category[0], category[1]))
    return response


def category_exists(url, cursor):
    """
        :param item_guid The guid of the item to retrieve the categories from the database.
        :type item_guid String
        :return The categories from the item with the specified guid.
    """
    result = cursor.execute('SELECT url, "text" FROM CATEGORY WHERE url=?', (url,))
    return result.fetchone() is not None



