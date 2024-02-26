from klass import Klass
from datetime import datetime, date
from requests import Session
from typing import Optional

fetchCourseURI = 'https://ehallapp.nju.edu.cn/gsapp/sys/yddwdkbapp/modules/wdkb/xspkjgcx.do'
fetchDateURI = 'https://ehallapp.nju.edu.cn/gsapp/sys/yddwdkbapp/modules/wdkb/getXnxqdyzc.do'
MAX_WEEK: int = 30

class Fetcher:
    LABEL_NAME = 'KCMC'
    LABEL_TEACHER = 'JSXM'
    LABEL_LOC = 'JASMC'
    LABEL_TIME_RANGE = 'ZCMC'
    LABEL_CODE = 'KCDM'
    LABEL_WEEKDAY = 'XQ'
    LABEL_START_TIME = 'KSSJ'
    LABEL_END_TIME = 'JSSJ'

    def __init__(self, session: Session, year: str, term: str, school_year: str):
        self.session: Session = session
        self.year: str = year
        self.term: str = term
        self.school_year: str = school_year

    def __parse_klass_data(self, data: dict, weekday2date: list[date]) -> Klass:
        STRPTIME_FORMAT: str = '%Y.%m.%d %H%M'
        weekday_idx: int = data[Fetcher.LABEL_WEEKDAY] - 1
        start_time: str = f'{self.year}.{weekday2date[weekday_idx]} {str(data[Fetcher.LABEL_START_TIME]).zfill(4)}'
        end_time: str = f'{self.year}.{weekday2date[weekday_idx]} {str(data[Fetcher.LABEL_END_TIME]).zfill(4)}'

        return Klass(name=data[Fetcher.LABEL_NAME],
                     teacher=data[Fetcher.LABEL_TEACHER],
                     loc=data[Fetcher.LABEL_LOC],
                     time_range=data[Fetcher.LABEL_TIME_RANGE],
                     code=data[Fetcher.LABEL_CODE],
                     start_time=datetime.strptime(start_time, STRPTIME_FORMAT),
                     end_time=datetime.strptime(end_time, STRPTIME_FORMAT),)

    def __fetch_weekday2date(self, week: str) -> Optional[list[date]]:
        data = {
            'xnxqdm': self.school_year + self.term,
            'zc': week,
        }

        r = self.session.post(fetchDateURI, data=data)
        resBody = r.json()
        return [item['RQ'] for item in resBody['rqData']] if 'rqData' in resBody else None

    def __fetch_klass_by_week(self, week: str) -> list[Klass]:
        weekday2date: Optional[list[date]] = self.__fetch_weekday2date(week)
        if weekday2date is None:
            return []

        data = {
            'XNXQDM': self.school_year + self.term,
            'DQZC': week,
        }

        r = self.session.post(fetchCourseURI, data=data)

        resBody = r.json()
        klass_data_rows: list[dict] = resBody['datas']['xspkjgcx']['rows']
        klasses: list[Klass] = [self.__parse_klass_data(class_data, weekday2date) for class_data in klass_data_rows]
        return klasses

    def fetch_all_klasses(self) -> list[Klass]:
        all_klasses = [klass for week in range(1, MAX_WEEK)
                             for klass in self.__fetch_klass_by_week(str(week))]
        return all_klasses
