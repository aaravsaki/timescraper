import db_helpers
import psycopg

DB_CONFIG = "dbconfig.json"

with psycopg.connect(db_helpers.get_connection_string()) as conn:
    with conn.cursor() as cur:
        cur.execute('DROP SCHEMA IF EXISTS uci CASCADE')

        cur.execute('CREATE SCHEMA IF NOT EXISTS uci')

        cur.execute("""
            CREATE TABLE uci.classroom (
                classroom_id serial PRIMARY KEY,
                building text NOT NULL,
                room_number text,
                UNIQUE (building, room_number)
                )
            """)

        cur.execute("""
            CREATE TYPE uci.day_of_week AS ENUM(
                'Su', 'M', 'Tu', 'W', 'Th', 'F', 'Sa'
            )
            """)

        cur.execute("""
            CREATE TABLE uci.meeting(
                meeting_id serial PRIMARY KEY,
                classroom_id integer,
                department_name text,
                course_number text,
                meeting_day uci.day_of_week[],
                meeting_start time,
                meeting_end time,
                FOREIGN KEY (classroom_id) REFERENCES uci.classroom(classroom_id)
            )
        """)
