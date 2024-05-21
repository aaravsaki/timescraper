import json
from pathlib import Path
import psycopg
from psycopg.rows import dict_row
from psycopg import sql
from typing import Optional

DB_CONFIG_PATH = 'dbconfig.json'

def get_connection_string() -> str:
    with Path(DB_CONFIG_PATH).open() as f:
        conn_params = [f'{key}={value}' for key, value in json.load(f).items()]
        conn_params = ' '.join(conn_params)
        return conn_params

def construct_insert(*, table_name: str, columns: list[str], returning: Optional[list[str]] = None) -> sql.Composed:
    if returning:
        return_sql = sql.SQL(', ').join(map(sql.Identifier, returning))
    else:
        return_sql = ''
    query = sql.SQL('INSERT INTO {table} ({}) VALUES ({}) ON CONFLICT DO NOTHING RETURNING ({})').format(
        sql.SQL(', ').join(map(sql.Identifier, columns)),
        sql.SQL(', ').join(sql.Placeholder() * len(columns)),
        return_sql,
        table=sql.Identifier('uci', table_name)
    )
    return query

def construct_select(*, table_name: str, columns: list[str], conditions: list[str]) -> sql.Composed:
    query = sql.SQL(('SELECT ({}) FROM {table} WHERE ' + 'AND '.join('{} = %s ' for _ in conditions))).format(
        sql.SQL(', ').join(map(sql.Identifier, columns)),
        *(sql.Identifier(condition) for condition in conditions),
        table=sql.Identifier('uci', table_name)
    )
    return query

def execute_query(sql: sql.Composed | sql.SQL, params=None, many=False):
    with psycopg.connect(get_connection_string(), row_factory=dict_row) as conn:
        cur = conn.execute(sql, params)
        if many:
            return cur.fetchall()
        return cur.fetchone()




