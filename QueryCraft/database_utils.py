import sqlite3
import os

def is_database_empty(db_name):
    """
    Checks if the SQLite database is empty (i.e., no tables exist).
    Returns True if the database is empty, otherwise False.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Check if there are any tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # If no tables exist, the database is empty
        return len(tables) == 0

    except sqlite3.Error as e:
        print(f"Error checking database: {e}")
        return False

    finally:
        # Close the database connection
        conn.close()


def load_sql_data(db_name, sql_file_path):
    """
    Loads SQL data from a file into the SQLite database.
    """
    try:
        # Resolve the absolute path of the SQL file
        sql_file_path = os.path.join(os.path.dirname(__file__), sql_file_path)

        # Connect to the SQLite database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Read the SQL file
        with open(sql_file_path, 'r', encoding='utf-8') as sql_file:
            sql_script = sql_file.read()

        # Execute the SQL script
        cursor.executescript(sql_script)
        conn.commit()
        print(f"SQL data from '{sql_file_path}' has been loaded into the database '{db_name}' successfully.")

    except sqlite3.Error as e:
        print(f"Error loading SQL data: {e}")

    except FileNotFoundError as e:
        print(f"Error: {e}")

    finally:
        # Close the database connection
        if 'conn' in locals():
            conn.close()


def extract_ddl_from_db(db_name):
    """
    Extracts the entire DDL (Data Definition Language) from the specified SQLite3 database.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Get the list of tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        ddl_statements = []

        for table in tables:
            table_name = table[0]

            # Get the CREATE TABLE statement for each table
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name}';")
            create_statement = cursor.fetchone()[0]
            ddl_statements.append(create_statement)

        return ddl_statements

    except sqlite3.Error as e:
        print(f"Error extracting DDL: {e}")
        return []

    finally:
        # Close the database connection
        if 'conn' in locals():
            conn.close()