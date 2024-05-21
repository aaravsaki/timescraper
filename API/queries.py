from datetime import datetime
from psycopg import sql
from db_helpers import construct_select, execute_query

MEETINGS_TABLE = 'meeting'
CLASSROOM_TABLE = 'classroom'

def _get_room_id(room: str):
    room_id = execute_query(
        construct_select(
            table_name=CLASSROOM_TABLE, 
            columns=['classroom_id'], 
            conditions=['building', 'room_number']
        ),
        params=room.split()
    )
    return room_id

def _current_day():
    day_mapping = {0: 'M', 1: 'Tu', 2: 'W', 3: 'Th', 4: 'F', 5: 'Sa', 6: 'Su'}
    return day_mapping[int(datetime.now().strftime('%w'))]

def current_meetings(room: str):
    query = sql.SQL('SELECT * FROM {table} WHERE classroom_id = %s AND meeting_start >= LOCALTIME AND meeting_end <= LOCALTIME').format(
        table=sql.Identifier('uci', MEETINGS_TABLE)
    )
    return execute_query(query, (_get_room_id(room),))

def empty_rooms():
    query = sql.SQL('SELECT CL.building, CL.room_number FROM uci.classroom CL \
    WHERE NOT EXISTS (SELECT * FROM uci.meeting ME WHERE ME.classroom_id = CL.classroom_id \
    AND ME.meeting_start <= LOCALTIME AND ME.meeting_end >= LOCALTIME AND {} = ANY(ME.meeting_day))').format(
        sql.Literal(_current_day())
    )
    return execute_query(query, many=True)



