from Crypto.Cipher import AES
import random
import base64
import string
import requests
import re
from io import BytesIO
from PIL import Image
from typing import Optional

NJUAuthURI = 'https://authserver.nju.edu.cn/authserver/login?service=https%3A%2F%2Fehallapp.nju.edu.cn%3A443%2Fgsapp%2Fsys%2Fyddwdkbapp%2F*default%2Findex.do%23%2Fwdkb'
NJUAuthCaptchURI = 'https://authserver.nju.edu.cn/authserver/captcha.html'

class NJUAuth:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0'
        })

        r = self.session.get(NJUAuthURI)
        self.lt = re.search(
            r'<input type="hidden" name="lt" value="(.*)"/>', r.text).group(1)
        self.execution = re.search(
            r'<input type="hidden" name="execution" value="(.*)"/>', r.text).group(1)
        self._eventId = re.search(
            r'<input type="hidden" name="_eventId" value="(.*)"/>', r.text).group(1)
        self.rmShown = re.search(
            r'<input type="hidden" name="rmShown" value="(.*)"', r.text).group(1)
        self.pwdDefaultEncryptSalt = re.search(
            r'<input type="hidden" id="pwdDefaultEncryptSalt" value="(.*)"', r.text).group(1)

    def getCaptchaCodeImage(self) -> Image:
        res = self.session.get(NJUAuthCaptchURI, stream=True)
        return Image.open(BytesIO(res.content))

    def __encryptPassword(self, password: str) -> str:
        random_iv = ''.join(random.sample((string.ascii_letters + string.digits) * 10, 16))
        random_str = ''.join(random.sample((string.ascii_letters + string.digits) * 10, 64))

        data = random_str + password
        key = self.pwdDefaultEncryptSalt.encode("utf-8")
        iv = random_iv.encode("utf-8")

        bs = AES.block_size
        pad = lambda s: s + (bs - len(s) % bs) * chr(bs - len(s) % bs)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        data = cipher.encrypt(pad(data).encode("utf-8"))
        return base64.b64encode(data).decode("utf-8")

    def needCaptcha(self, username: str) -> bool:
        url = f'https://authserver.nju.edu.cn/authserver/needCaptcha.html?username={username}'
        r = self.session.post(url)
        return 'true' in r.text

    def login(self, username: str, password: str, captchaResponse:str="") -> Optional[str]:
        data = {
            'username': username,
            'password': self.__encryptPassword(password),
            'lt': self.lt,
            'dllt': 'userNamePasswordLogin',
            'execution': self.execution,
            '_eventId': self._eventId,
            'rmShown': self.rmShown,
            'captchaResponse': captchaResponse,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome"
        }
        r = self.session.post(NJUAuthURI, data=data)
        return len(r.history) > 0
