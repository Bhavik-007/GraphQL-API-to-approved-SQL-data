import sqlite3
import tomllib


# ============================================================
# LOAD CONFIGURATION
# ============================================================

with open("config.toml", "rb") as file:
    config = tomllib.load(file)


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_PATH = config["database"]["path"]


# ============================================================
# GRAPHQL CONFIGURATION
# ============================================================

ALLOWED_TABLES = set(
    config["graphql"]["allowed_tables"]
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    connection = sqlite3.connect(
        DB_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# VALIDATE TABLE
# ============================================================

def validate_table(table_name: str):

    if table_name not in ALLOWED_TABLES:

        raise ValueError(
            f"Table '{table_name}' is not allowed."
        )


# ============================================================
# GET ALLOWED TABLES
# ============================================================

def get_allowed_tables():

    return sorted(
        ALLOWED_TABLES
    )


# ============================================================
# GET TABLE DATA
# ============================================================

def get_table_data(
    table_name: str,
    limit: int = 1000
):

    validate_table(table_name)

    connection = get_connection()

    try:

        cursor = connection.execute(
            f'''
            SELECT *
            FROM "{table_name}"
            LIMIT ?
            ''',
            (limit,)
        )

        columns = [
            description[0]
            for description in cursor.description
        ]

        rows = [
            dict(row)
            for row in cursor.fetchall()
        ]

        return columns, rows

    finally:

        connection.close()


# ============================================================
# GET TABLE COLUMN INFORMATION
# ============================================================

def get_table_columns(table_name: str):

    validate_table(table_name)

    connection = get_connection()

    try:

        cursor = connection.execute(
            f'''
            PRAGMA table_info("{table_name}")
            '''
        )

        result = []

        for row in cursor.fetchall():

            result.append(
                {
                    "name": row["name"],
                    "type": row["type"]
                }
            )

        return result

    finally:

        connection.close()