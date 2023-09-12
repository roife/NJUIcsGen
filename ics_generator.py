from klass import Klass
from datetime import datetime

class ICSGenerator:
    def __get_ics_payload_header(title: str) -> str:
        return f"""BEGIN:VCALENDAR
VERSION:2.0
X-WR-CALNAME:{title}
CALSCALE:GREGORIAN
BEGIN:VTIMEZONE
TZID:Asia/Shanghai
TZURL:http://tzurl.org/zoneinfo-outlook/Asia/Shanghai
X-LIC-LOCATION:Asia/Shanghai
BEGIN:STANDARD
TZOFFSETFROM:+0800
TZOFFSETTO:+0800
TZNAME:CST
DTSTART:19700101T000000
END:STANDARD
END:VTIMEZONE"""

    def __get_event_info(klass: Klass) -> str:
        event_start = datetime.strftime(klass.start_time, '%Y%m%dT%H%M%S')
        event_end = datetime.strftime(klass.end_time, '%Y%m%dT%H%M%S')
        event_description = f"""课程编号：{klass.code}
名称：{klass.name}
教师：{klass.teacher}
教学周期：{klass.time_range}"""
        event_description = event_description.replace('\n', '\\n')

        return f"""
BEGIN:VEVENT
DESCRIPTION:{event_description}
DTSTART;TZID=Asia/Shanghai:{event_start}
DTEND;TZID=Asia/Shanghai:{event_end}
LOCATION:{klass.loc}
SUMMARY:{klass.name}
BEGIN:VALARM
TRIGGER:-PT30M
REPEAT:1
DURATION:PT1M
END:VALARM
END:VEVENT"""

    def __get_ics_payload_footer() -> str:
        return "\nEND:VCALENDAR"

    def generate_ics(title: str, klasses: list[Klass]) -> str:
        ics_payload: str = ICSGenerator.__get_ics_payload_header(title)

        for klass in klasses:
            ics_payload += ICSGenerator.__get_event_info(klass)

        ics_payload += ICSGenerator.__get_ics_payload_footer()
        return ics_payload