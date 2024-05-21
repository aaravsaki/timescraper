from datetime import datetime
import requests
from typing import Iterator
import re

COURSES_URL = 'https://api.peterportal.org/rest/v0/courses/all'
SCHEDULE_URL = 'https://api.peterportal.org/rest/v0/schedule/soc'

class Meeting():
    def __init__(self, dept_code: str, course_number: str, building: str, days: str, time: str):
        self.dept_code = dept_code
        self.course_number = course_number
        self.building = building
        self.days = Meeting.format_days(days)
        self.format_time(time)

    def format_time(self, time: str):
        times = time.strip().split()
        start = times[0][:-1]
        end = times[1]

        if end[-1] == 'p':
            if int(start[:start.index(':')]) == 12 or int(start[:start.index(':')]) <= int(end[:end.index(':')]):
                start += ' PM'
            else:
                start += ' AM'
            end = end[:-1] + ' PM'
        else:
            start += ' AM'
            end = end[:-1] + ' AM'

        self.start_time = datetime.strptime(start, '%I:%M %p').time()
        self.end_time = datetime.strptime(end, '%I:%M %p').time()

    @staticmethod
    def format_days(days: str) -> list[str]:
        return re.findall('[A-Z][^A-Z]*', days)


def get_classes() -> Iterator[tuple[str, str]]:
    """Returns all unique department and number combinations that denote existing classes at UCI."""
    response = requests.get(COURSES_URL).json()
    course_codes = {(listing['department'], listing['number']) for listing in response}
    yield from course_codes

def get_meetings(term: str) -> Iterator[Meeting]:
    """
    Returns all UCI class meetings.

    Arguments:
    term - string denoting schedule term, i.e. '2024 Spring'
    classes - list of (department, course_number) tuples
    """
    classes = get_classes()
    for listing in classes:
        department, number = listing
        payload = {'term': term, 'department': department, 'courseNumber': number}
        response = requests.get(SCHEDULE_URL, params=payload).json()
        try:
            for school in response['schools']:
                for department in school['departments']:
                    for course in department['courses']:
                        for section in course['sections']:
                            for meeting in section['meetings']:
                                if len(meeting['bldg'].split()) == 2:
                                    yield Meeting(course['deptCode'], course['courseNumber'], meeting['bldg'], meeting['days'], meeting['time'])
        except (KeyError, IndexError):
            pass

