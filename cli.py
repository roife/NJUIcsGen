from klass import Klass
from fetcher import Fetcher
from ics_generator import ICSGenerator
from nju_auth import NJUAuth

import getpass
from datetime import datetime

def loginAndGetSession() -> str:
    auth: NJUAuth = NJUAuth()

    username: str = input('Please input your student ID: ')
    password: str = getpass.getpass('Please input your password: ')
    captchaResponse: str = ''

    if auth.needCaptcha(username):
        auth.getCaptchaCodeImage().show()
        captchaResponse = input('Please input captcha code: ')

    if auth.login(username, password, captchaResponse):
        print('Login successfully')
        return auth.session
    else:
        print('Login failed')
        exit(1)

def mergeAdjacentKlasses(klasses: list[Klass]) -> list[Klass]:
    klasses = sorted(klasses, key=lambda klass: klass.start_time)
    i: int = 1
    while i < len(klasses):
        if klasses[i].name == klasses[i-1].name:
            klasses[i-1].end_time = klasses[i].end_time
            klasses.pop(i)
        else:
            i += 1
    return klasses

if __name__ == '__main__':
    year: str = str(datetime.now().year)
    term: str = '2' if datetime.now().month < 9 else '1'

    session: str = loginAndGetSession()
    klasses: list[Klass] = Fetcher(session, year, term).fetch_all_klasses()
    klasses = mergeAdjacentKlasses(klasses)

    with open('classes.ics', 'w+', encoding='utf-8') as f:
        f.write(ICSGenerator.generate_ics(f'南京大学 {year} 第 {term} 学期课程表', klasses))