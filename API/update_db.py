from db_helpers import construct_select, construct_insert, execute_query
import process_data

LIMIT_RECORDS = 30
record_count = 0

for result in process_data.get_meetings('2023 Winter'):
    if record_count > LIMIT_RECORDS:
        break
    if result.building == 'ONLINE' or result.building == 'TBA':
        continue

    class_id = execute_query(
        construct_insert(
            table_name='classroom', columns=['building', 'room_number'],
            returning=['classroom_id']), params=result.building.split()
    )
    if class_id:
        class_id = class_id['classroom_id']
        record_count += 1
    else:
        class_id = execute_query(
            construct_select(
                table_name='classroom', columns=['classroom_id'], 
                conditions=['building', 'room_number']), params=result.building.split()
        )
        class_id = class_id['classroom_id'] if class_id else None

    execute_query(
        construct_insert(
            table_name='meeting',
            columns=['classroom_id', 'department_name', 'course_number', 'meeting_day', 'meeting_start', 'meeting_end'],
        ),
        params=[class_id, result.dept_code, result.course_number, result.days, result.start_time, result.end_time]
    )



